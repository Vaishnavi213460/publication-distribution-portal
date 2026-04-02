from django.shortcuts import render, redirect
from admin_panel.models import Frequency, Product, Supplier
from login.models import Agent
from .forms import AgentSuppForm

def agent_dashboard(request):
    return render(request, 'agentheader.html')

def agent_freq_view(request):
    context = {}

    context['list'] = Frequency.objects.all()
    return render(request, "agent_freq_view.html", context)

def agent_pdt_view(request):
    context = {}

    context['list'] = Product.objects.all()
    return render(request, "agent_pdt_view.html", context)

def agent_supp_view(request):
    context = {}

    context['list'] = Supplier.objects.all()
    return render(request, "agent_supp_view.html", context)


def add_agent_supplier(request):
    context = {}
    form = AgentSuppForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)

        # get agent using logged-in user
        agent = Agent.objects.get(login=request.user)

        obj.agent = agent
        obj.save()

        return redirect(agent_dashboard)
    context['form'] = form
    return render(request, "add_agent_supp_form.html", context)
