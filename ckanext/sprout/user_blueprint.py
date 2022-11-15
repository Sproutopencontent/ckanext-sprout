import ckan.lib.helpers as h
import flask 
from flask import send_file, Response
from ckan.common import g
import ckan.plugins.toolkit as toolkit
import pandas as pd
from pathlib import Path

sp_user = flask.Blueprint('sp_user', __name__)

def download_profiles():
    user_obj = g.userobj
    if user_obj and user_obj.sysadmin:

        y=str(Path().absolute())
        users_list = toolkit.get_action('user_list')({},{})
        df = pd.DataFrame(users_list)
        df.to_csv('profiles.csv', index=False)
    
    else:
        return Response("Page Not Found", status=400,)

    return send_file( y + '/profiles.csv', mimetype='text/csv' , as_attachment=True)
    
    


sp_user.add_url_rule(u'/download_profiles', view_func=download_profiles)