from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from social.models import Member, Profile, Message
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
import operator
import os.path
from django.template import RequestContext
from django.shortcuts import render_to_response


# Enables ImageFile objects
from django.core.files.images import ImageFile
# Enable Coursework configs
from social import configs
# Enables Flash Cards
from django.contrib import messages as flash

appname = 'Facemagazine'

# decorator that tests whether user is logged in
def loggedin(f):
    def test(request):
        if 'username' in request.session:
            return f(request)
        else:
            template = loader.get_template('social/not-logged-in.html')
            context = RequestContext(request, {})
            return HttpResponse(template.render(context))
    return test

def index(request):
    template = loader.get_template('social/index.html')
    
    context = RequestContext(request, {
    		'appname': appname,
    	})
    return HttpResponse(template.render(context))

def signup(request):
    template = loader.get_template('social/signup.html')
    context = RequestContext(request, {
    		'appname': appname,
    	})
    return HttpResponse(template.render(context))

def register(request):
    u = request.POST['user']
    p = request.POST['pass']
    user = Member(username=u, password=p)
    user.save()
    template = loader.get_template('social/user-registered.html')    
    context = RequestContext(request, {
        'appname': appname,
        'username' : u
        })
    return HttpResponse(template.render(context))

def login(request):
    if 'username' not in request.POST:
        template = loader.get_template('social/login.html')
        context = RequestContext(request, {
                'appname': appname,
            })
        return HttpResponse(template.render(context))
    else:
        u = request.POST['username']
        p = request.POST['password']
        try:
            member = Member.objects.get(pk=u)
        except Member.DoesNotExist:
            raise Http404("User does not exist")
        if p == member.password:
            request.session['username'] = u;
            request.session['password'] = p;
            return render(request, 'social/login.html', {
                'appname': appname,
                'username': u,
                'loggedin': True}
                )
        else:
            return HttpResponse("Wrong password") 

@loggedin
def search_form(request):
    template = loader.get_template('social/search_form.html')
    context = RequestContext(request, {
        'appname': appname,
    })
    return HttpResponse(template.render(context))
   

"""def search(request):
    if 'q' in request.GET:
        message = 'You searched for: %r' % request.GET['q']
    else:
        message = 'You submitted an empty form.'
    return HttpResponse(message)"""
@loggedin
def search(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        members = Member.objects.filter(username__icontains=q)
        return render(request, 'social/members.html',
            {'members': members, 'query': q})
       # return HttpResponseRedirect('social/members.html')
    else:
        return HttpResponse('Please submit a search term.')

@loggedin
def friends(request):
    username = request.session['username']
    member_obj = Member.objects.get(pk=username)
    # list of people I'm following
    following = member_obj.following.all()
    # list of people that are following me
    followers = Member.objects.filter(following__username=username)
    # render reponse
    return render(request, 'social/friends.html', {
        'appname': appname,
        'username': username,
        'members': members,
        'following': following,
        'followers': followers,
        'loggedin': True}
        )

@loggedin
def logout(request):
    if 'username' in request.session:
        u = request.session['username']
        request.session.flush()        
        template = loader.get_template('social/logout.html')
        context = RequestContext(request, {
                'appname': appname,
                'username': u
            })
        return HttpResponse(template.render(context))
    else:
        raise Http404("Can't logout, you are not logged in")

def member(request, view_user):
    username = request.session['username']
    member = Member.objects.get(pk=view_user)
    data = {}

    if view_user == username:
        greeting = "Your"
    else:
        greeting = view_user + "'s"

    # Put all data which will be used on view on the data array (if there is a profile created)
    if member.profile:
        data['text']      = member.profile.text
        data['country']   = member.profile.country
        data['city']      = member.profile.city
        data['workplace'] = member.profile.workplace
        data['phone']     = member.profile.phone
        data['picture']   = member.profile.picture
    else:
        data['text']      = None
        data['country']   = None
        data['city']      = None
        data['workplace'] = None
        data['phone']     = None
        data['picture']   = None

    return render(request, 'social/member.html', {
        'appname': appname,
        'username': username,
        'view_user': view_user,
        'greeting': greeting,
        'data': data,
        'loggedin': True}
        )

@loggedin
def members(request):
    username = request.session['username']
    member_obj = Member.objects.get(pk=username)
    # follow new friend
    if 'add' in request.GET:
        friend = request.GET['add']
        friend_obj = Member.objects.get(pk=friend)
        member_obj.following.add(friend_obj)
        member_obj.save()
    # unfollow a friend
    if 'remove' in request.GET:
        friend = request.GET['remove']
        friend_obj = Member.objects.get(pk=friend)
        member_obj.following.remove(friend_obj)
        member_obj.save()
    # view user profile
    if 'view' in request.GET:
        return member(request, request.GET['view'])
    else:
        # list of all other members
        members = Member.objects.exclude(pk=username)
        # list of people I'm following
        following = member_obj.following.all()
        # list of people that are following me
        followers = Member.objects.filter(following__username=username)
        # render reponse
        return render(request, 'social/members.html', {
            'appname': appname,
            'username': username,
            'members': members,
            'following': following,
            'followers': followers,
            'loggedin': True}
            )

def checkPictureSize(picture):
    if picture.width > configs.max_width_profile or picture.height > configs.max_height_profile:
        raise ValidationError('Picture dimensions not allowed! Only up to 800x600.')
        return False

    return True

def checkPictureExtension(picture):
    # Check extension name    
    ext = os.path.splitext(picture.name)[1]  # [0] returns path+filename

    # If is not enabled, return false
    if not ext in configs.valid_extensions:
        #raise ValidationError('Unsupported file extension.')
        return False;

    return True


@loggedin
def profile(request):
    u = request.session['username']
    data = {}
    member = Member.objects.get(pk=u)
    if request.POST:
        # Get all the posted data
        text      = request.POST['text']
        country   = request.POST['country']
        city      = request.POST['city']
        workplace = request.POST['workplace']
        phone     = request.POST['phone']
        
        # If a picture was uploaded, treat it... otherwise, just insert a null object
        if 'picture' in request.FILES:
            # Create a ImageFile object
            picture   = ImageFile(request.FILES['picture'])
            # Check if the picture is inside the configured settings
            # If is not, it just delete the ImageFile object
            if checkPictureSize(picture) == False:
                picture = None
                flash.error(request, 'Picture dimensions not allowed! Only up to 800x600.')
            elif checkPictureExtension(picture) == False:
                picture = None
                flash.error(request, 'Format not allowed! Only gif, jpeg and png.') 
        else:
            picture = None

        if member.profile:
            member.profile.text      = text
            member.profile.country   = country
            member.profile.city      = city
            member.profile.workplace = workplace
            member.profile.phone     = phone

            # If there was a uploaded picture which respects the settings
            if picture != None:
                member.profile.picture.save(request.FILES['picture'].name, picture)

            member.profile.save()
        else:
            profile = Profile(text=text, country=country, city=city, workplace=workplace, phone=phone, picture=picture)
            profile.save()
            member.profile = profile

        member.save()
    
    # Put all data which will be used on view on the data array (if there is a profile created)
    if member.profile:
        data['text']      = member.profile.text
        data['country']   = member.profile.country
        data['city']      = member.profile.city
        data['workplace'] = member.profile.workplace
        data['phone']     = member.profile.phone
        data['picture']   = member.profile.picture
    else:
        data['text']      = None
        data['country']   = None
        data['city']      = None
        data['workplace'] = None
        data['phone']     = None
        data['picture']   = None

    return render(request, 'social/profile.html', {
        'appname': appname,
        'username': u,
        'data': data,
        'loggedin': True
    })

@loggedin
def messages(request):
    username = request.session['username']
    user = Member.objects.get(pk=username)
    # Whose message's are we viewing?
    if 'view' in request.GET:
        view = request.GET['view']
    else:
        view = username
    recip = Member.objects.get(pk=view)
    # If message was deleted
    if 'erase' in request.GET:
        msg_id = request.GET['erase']
        Message.objects.get(id=msg_id).delete()
    # If text was posted then save on DB
    if 'text' in request.POST:
        text = request.POST['text']
        pm = request.POST['pm'] == "0"
        message = Message(user=user,recip=recip,pm=pm,time=timezone.now(),text=text)
        message.save()
    messages = Message.objects.filter(recip=recip)
    profile_obj = Member.objects.get(pk=view).profile
    profile = profile_obj.text if profile_obj else ""
    return render(request, 'social/messages.html', {
        'appname': appname,
        'username': username,
        'profile': profile,
        'view': view,
        'messages': messages,
        'loggedin': True}
        )

@loggedin
def upload_picture(request):
    try:
        f = request.FILES['picture']
        ext = os.path.splitext(f.name)[1].lower()
        valid_extensions = ['.gif', '.png', '.jpg', '.jpeg', '.bmp']
        if ext in valid_extensions:
            filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '_tmp.jpg'
            with open(filename, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            im = Image.open(filename)
            width, height = im.size
            if width > 560:
                new_width = 560
                new_height = (height * 560) / width
                new_size = new_width, new_height
                im.thumbnail(new_size, Image.ANTIALIAS)
                im.save(filename)
            return redirect('/settings/picture/?upload_picture=uploaded')
        else:
            messages.error(request, u'Invalid file format.')
    except Exception:
        messages.error(request, u'An expected error occurred.')
    return redirect('/settings/picture/')


def checkuser(request):
    if 'user' in request.POST:
        u = request.POST['user']
        try:
            member = Member.objects.get(pk=u)
        except Member.DoesNotExist:
            member = None
        if member is not None:
            return HttpResponse("<span class='taken'>&nbsp;&#x2718; This username is taken</span>")
        else:
            return HttpResponse("<span class='available'>&nbsp;&#x2714; This username is available</span>")
