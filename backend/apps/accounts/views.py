import hashlib
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse
class ThrottledLoginView(LoginView):
    template_name="registration/login.html"; max_attempts=5; lock_seconds=900
    def key(self):
        value=f'{self.request.META.get("REMOTE_ADDR","")}:{self.request.POST.get("username","").lower()}'; return "login:"+hashlib.sha256(value.encode()).hexdigest()
    def dispatch(self,request,*args,**kwargs):
        if request.method=="POST" and cache.get(self.key(),0)>=self.max_attempts: return HttpResponse("Too many login attempts. Try again later.",status=429)
        return super().dispatch(request,*args,**kwargs)
    def form_invalid(self,form):
        key=self.key(); cache.set(key,cache.get(key,0)+1,self.lock_seconds); return super().form_invalid(form)
    def form_valid(self,form):
        cache.delete(self.key()); return super().form_valid(form)
