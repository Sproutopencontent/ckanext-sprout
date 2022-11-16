import ckan.lib.helpers as h
import flask, requests, os
from flask import send_file, Response
from ckan.common import g
import ckan.plugins.toolkit as toolkit
from pathlib import Path
from flask import after_this_request

sp_user = flask.Blueprint('sp_user', __name__)

def download_profiles():
    user_obj = g.userobj
    if user_obj and user_obj.sysadmin:
        y=str(Path().absolute())
        users_list = toolkit.get_action('user_list')({},{})
        
        for i in range(len(users_list)):
            with open('profiles.csv','w') as f:
                f.write(','.join(users_list[0].keys()))
                f.write('\n')
                for row in users_list:
                    f.write(','.join(str(x) for x in row.values()))
                    f.write('\n')
                f.close()
        @after_this_request
        def remove_file(response):
            os.remove('profiles.csv')
            return response

    else:
        return Response("Page Not Found", status=400,)

    return send_file( y + '/profiles.csv', mimetype='text/csv' , as_attachment=True)
    
    
sp_user.add_url_rule(u'/download_profiles', view_func=download_profiles)