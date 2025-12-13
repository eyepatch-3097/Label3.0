from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import LoginForm, SignupStep1Form, SignupOrgForm
from .models import Org, User, OrgJoinRequest
from .utils import split_email_domain, is_generic_email_domain
from django.db import transaction


class LabelcraftLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'


def logout_view(request):
    logout(request)
    return redirect('login')


@require_http_methods(["GET", "POST"])
def signup_step1(request):
    """
    Step 1: email + password only.
    Logic:
    - If company domain & org exists -> create pending user + join request + show pending msg
    - Else (generic OR first company user) -> stash email+password in session -> redirect to signup_org
    """
    if request.method == "POST":
        form = SignupStep1Form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            domain = split_email_domain(email)

            existing_org = None
            if not is_generic_email_domain(domain):
                existing_org = Org.objects.filter(domain=domain).first()

            if existing_org:
                # Company org already exists -> create pending user & join request
                with transaction.atomic():
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        org=existing_org,
                        role=User.ROLE_OPERATOR,
                        status=User.STATUS_PENDING,
                    )
                    OrgJoinRequest.objects.create(org=existing_org, user=user)

                # TODO: send actual email notification to org admin(s)
                return render(request, 'accounts/signup_pending.html', {
                    "org": existing_org,
                    "email": email,
                })

            # Else: generic OR first company user -> go to org step
            request.session['signup_email'] = email
            request.session['signup_password'] = password
            request.session['signup_domain'] = domain
            return redirect('signup_org')
    else:
        form = SignupStep1Form()

    return render(request, 'accounts/signup_step1.html', {"form": form})


@require_http_methods(["GET", "POST"])
def signup_org(request):
    """
    Step 2: ask for Org Name, then create org + admin user.
    Handles:
    - generic email domains
    - first user for a company domain
    """
    email = request.session.get('signup_email')
    password = request.session.get('signup_password')
    domain = request.session.get('signup_domain')

    if not email or not password:
        # If step1 data missing, send back to step1
        return redirect('signup')

    if request.method == "POST":
        form = SignupOrgForm(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['org_name']

            with transaction.atomic():
                org_domain = None if is_generic_email_domain(domain) else domain

                org, created = Org.objects.get_or_create(
                    domain=org_domain,
                    defaults={"name": org_name},
                )
                # If org existed but had no name, we could update it (edge case)
                if not created and not org.name:
                    org.name = org_name
                    org.save()

                user = User.objects.create_user(
                    email=email,
                    password=password,
                    org=org,
                    role=User.ROLE_ADMIN,
                    status=User.STATUS_ACTIVE,
                )

            # Clean up session
            for key in ['signup_email', 'signup_password', 'signup_domain']:
                request.session.pop(key, None)

            # Auto-login the new admin
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupOrgForm()

    return render(request, 'accounts/signup_org.html', {
        "form": form,
        "email": email,
    })

@login_required
def org_join_requests_list(request):
    """
    List pending join requests for the current user's organisation.
    Only accessible to org admins.
    """
    user = request.user

    if not user.org or user.role != User.ROLE_ADMIN:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')

    pending_requests = OrgJoinRequest.objects.filter(
        org=user.org,
        is_approved=False,
        user__status=User.STATUS_PENDING,
    ).select_related('user')

    return render(request, 'accounts/org_requests.html', {
        "pending_requests": pending_requests,
        "org": user.org,
    })


@login_required
@require_http_methods(["POST"])
def approve_org_join_request(request, request_id):
    """
    Approve a pending join request in the current admin's organisation.
    - Marks join request as approved
    - Sets user.status = ACTIVE
    """
    user = request.user

    if not user.org or user.role != User.ROLE_ADMIN:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('dashboard')

    join_request = get_object_or_404(
        OrgJoinRequest,
        id=request_id,
        org=user.org,
        is_approved=False,
    )

    # Approve
    join_request.is_approved = True
    join_request.save()

    join_user = join_request.user
    join_user.status = User.STATUS_ACTIVE
    join_user.save()

    # TODO: optional – send email notification to join_user

    messages.success(request, f"{join_user.email} has been approved and can now use Labelcraft.")
    return redirect('org_join_requests')
