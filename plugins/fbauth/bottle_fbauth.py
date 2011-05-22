import inspect
import facebook
from bottle import request, abort

class FBAuthPlugin(object):
    ''' This plugin determines if a Facebook user is logged in and returns the
    user context if they are.
    
    @routes that that accept a `fb_user` keyword argument (or a custom value)
    will automatically get a user cookie. The plug-in will only attempt to
    authenticate a user if the keyword is present. The developer can control
    the behavior of the application when user is not logged in by checking
    if `fb_user` is None, or specify fail_without_user=True to have the plugin
    automatically send abort(401, ...). The cookie can be used in conjunction
    with the Facebook API to get user information. Alternatively, you can 
    specify a user_resolver method during set which will be called to create a
    user object of your choice.
    
    You will also need to download the Facebook Python SDK and include 
    facebook.py in your sys.path for this plugin to work. You can download it
    here: 
     
        http://github.com/facebook/python-sdk
        
    For more information on how to use the cookie to retrieve information from
    the Facebook GraphAPI, see the Python SDK's examples:
    
    https://github.com/facebook/python-sdk/tree/master/examples/appengine

            :param fb_app_id: Provided when you set up your application on 
            developer.facebook.com.
            :param fb_app_secret: Also provided on developer.facebook.com
            :param user_resolver: A callback which is used to resolve the FB
            cookie into a user object of your choosing. If None is specified,
            the cookie is returned directly to the @route (default is None)
            :param fail_without_user: If True, the plugin will call 
            abort(401, ...) automatically if no user is logged in (default
            is False)
            :param user_override: For testing purposes, you can provide a fixed 
            user object to return instead of doing authentication (default is 
            None)
            :param keyword: fb_user is the default keyword, but an alternative
            can be specified.
    '''

    name = 'fbauth'

    def __init__(self, fb_app_id, fb_app_secret, user_resolver=None, fail_without_user=False, user_override=None, keyword='fb_user'):
         self.app_id = fb_app_id
         self.app_secret = fb_app_secret
         self.resolver = user_resolver
         self.fail_without_user = fail_without_user
         self.user_override = user_override
         self.keyword = keyword
         
    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, FBAuthPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another FBAuth plugin with \
                    conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        # Override global configuration with route-specific values.
        conf = context['config'].get('fbauth') or {}
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'user' keyword.
        # Ignore it if it does not need a logged in user.
        args = inspect.getargspec(context['callback'])[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            
            fb_user = None
            if self.user_override:
                fb_user = self.user_override
            else:
                fb_user = facebook.get_user_from_cookie(request.COOKIES, 
                    self.app_id, self.app_secret)
            
                # If fail fast is set, abort the call immediately
                if self.fail_without_user and not fb_user:
                    abort(401, 'Facebook user not logged in')
            
                # If developer has set a custom user resolver, use it 
                # to resolve the cookie to a real instance
                if self.resolver and fb_user:
                    fb_user = self.resolver(fb_user)
                
            kwargs[keyword] = fb_user
            
            rv = callback(*args, **kwargs)
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper

Plugin = FBAuthPlugin