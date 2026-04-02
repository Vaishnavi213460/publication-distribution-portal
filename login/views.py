from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from .forms import AgentForm, CustomerForm
from .models import Role

def home(request):
    return HttpResponse(
        "Hi <br><a href='/agent_registration/'>Agent Registration</a><br>"
        "<a href='/login/'>Login</a>"
    )

def customer_home(request):
    return HttpResponse("Welcome Customer")


# ---------------- AGENT REGISTRATION ----------------
def agent_registration(request):
    context = {}
    frm = AgentForm(request.POST or None,request.FILES or None)

    if frm.is_valid():
        # Get data from form
        username = frm.cleaned_data['Username']
        password = frm.cleaned_data['Password']

        # Create Django auth user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # Save agent details
        obj = frm.save(commit=False)
        obj.login = user
        obj.save()

        frm.instance = obj
        frm.save_m2m()

        # Create Role
        Role.objects.create(role='Agent', login=user)

        return HttpResponseRedirect('/login/login/')

    context['form'] = frm
    return render(request, 'agent_insert.html', context)


# ---------------- CUSTOMER REGISTRATION ----------------
def customer_registration(request):
    context = {}
    frm = CustomerForm(request.POST or None,request.FILES or None)

    if frm.is_valid():
        # Get data from form
        username = frm.cleaned_data['Username']
        password = frm.cleaned_data['Password']

        # Create Django auth user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # Save Customer details
        obj = frm.save(commit=False)
        obj.login = user
        obj.save()

        # Create Role
        Role.objects.create(role='Customer', login=user)

        return HttpResponseRedirect('/login/login/')

    context['form'] = frm
    return render(request, 'customer_insert.html', context)




# ---------------- LOGIN ----------------
def login_user(request):
    if request.method == "POST":
        uname = request.POST.get("Username")
        pd = request.POST.get("pwd")

        user_obj = authenticate(username=uname, password=pd)

        if user_obj is not None:
            auth_login(request, user_obj)
            user_id = user_obj.id

            if user_obj.is_superuser is True:
                # return HttpResponseRedirect('/admin_panel')
                return redirect('/admin_panel')

            role_obj = Role.objects.get(login=user_id)

            RoleType = role_obj.role

            if RoleType == 'Agent':
                # return HttpResponseRedirect('/agent_home/')
                return redirect('agent_dashboard')
            elif RoleType == 'Customer':
                # return HttpResponseRedirect('/customer_home/')
                return redirect('customer_dashboard')
        else:
            return HttpResponse("<script>alert('Invalid Credential !!!');window.location='/';</script>")

    return render(request, 'login.html')
