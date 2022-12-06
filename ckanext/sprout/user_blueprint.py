import ckan.lib.helpers as h
import csv
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

        # create the csv with the complete user data
        for i in range(len(users_list)):
            with open('profiles.csv','w') as f:
                f.write(','.join(users_list[0].keys()))
                f.write('\n')
                for row in users_list:
                    f.write(','.join(str(x) for x in row.values()))
                    f.write('\n')
                f.close()
        
        # remove the unwanted columns from the csv
        with open('profiles.csv') as instream:
            # setup the input
            reader = csv.DictReader(instream)
            rows = list(reader)
            # Setup the output fields
            output_fields = reader.fieldnames
            output_fields.remove("email_hash")
            output_fields.remove("apikey")
        
        with open("profiles.csv", "w") as outstream:
            # setup the output
            writer = csv.DictWriter(
                    outstream,
                    fieldnames=output_fields,
                    extrasaction="ignore",  # Ignore extra dictionary keys/values
                )

            # Write to the output
            writer.writeheader()
            writer.writerows(rows)
           
            
            instream.close()
            outstream.close()
        
        @after_this_request
        def remove_file(response):
            os.remove('profiles.csv')
            return response

    else:
        return Response("Page Not Found", status=404,)

    return send_file( y + '/profiles.csv', mimetype='text/csv' , as_attachment=True)
    
    
sp_user.add_url_rule(u'/download_profiles', view_func=download_profiles)