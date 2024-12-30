from decimal import Decimal
from rest_framework import renderers
import json

class CustomRenderer(renderers.JSONRenderer):
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):

        def decimal_to_float(value):
            if isinstance(value, Decimal):
                return float(value)
            elif isinstance(value, dict):
                return {k: decimal_to_float(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [decimal_to_float(v) for v in value]
            else:
                return value

        # Convert Decimals in data to floats
        data = decimal_to_float(data)

        response = {}
        print(data)

        response['status'] = True
        response['message'] = data.get('message', 'Request was successful.')
        response['status_code'] = data.get('status_code', 200)
        for key in ['message', 'status_code']:
            data.pop(key, None)
        response['data'] = data
        
        if isinstance(data, dict):
            if 'errors' in data and 'ErrorDetail' not in str(data):
                response['status'] = False
                response['status_code'] = data['errors'].get('status_code')
                response['message'] = 'An error occurred'
                errors = data['errors'].copy() 
                if 'status_code' in errors:
                    del errors['status_code']
                
                response['errors'] = errors
                response['data'] = None

    
            elif 'errors' in data and 'ErrorDetail' in str(data) and 'invalid' not in str(data) and 'unique' not in str(data):
                response['status'] = False
                response['status_code'] = data.get('status_code', 400)
                response['message'] = 'An error occurred'
                error_details = {}
                for field, errors in data['errors'].items():
                    if isinstance(errors, list) and errors:
                        error_details['error'] = f"{field.replace('_', ' ').capitalize()} is required."
                    else:
                        error_details['error'] = f"{field.replace('_', ' ').capitalize()} is required."
                    
                response['errors'] = error_details
                response['data'] = None

            elif 'errors' in data and 'ErrorDetail' in str(data) and 'unique' in str(data):
                response['status'] = False
                response['status_code'] = data.get('status_code', 200)
                response['message'] = 'An error occurred'
                error_details = {}
                for field, errors in data['errors'].items():
                    if isinstance(errors, list) and errors:
                        error_details['error'] = f"{errors[0]}"
                    else:
                        error_details['error'] = f"{str(errors)}"

                response['errors'] = error_details
                response['data'] = None
            
            elif 'errors' in data and 'ErrorDetail' in str(data) and 'invalid' in str(data):
                response['status'] = False
                response['status_code'] = data.get('status_code', 400)
                response['message'] = 'An error occurred'
                error_details = {}
                for field, errors in data['errors'].items():
                    if isinstance(errors, list) and errors:
                        error_details['error'] = f"{errors[0]}"
                    else:
                        error_details['error'] = f"{str(errors)}"

                response['errors'] = error_details
                response['data'] = None

            elif 'detail' in data and 'Authentication' in str(data):
                response['status'] = False
                response['message'] = 'A detailed error occurred.'
                response['status_code'] = data.get('status_code', 401)
                response['data'] = None
                response['errors'] = data.get('detail', 'A detailed error occurred.')
            
            elif 'detail' in data and 'Authorization' in str(data):
                response['status'] = False
                response['message'] = 'A detailed error occurred.'
                response['status_code'] = data.get('status_code', 401)
                response['data'] = None
                response['errors'] = data.get('detail', 'A detailed error occurred.')
            
            elif 'detail' in data and 'ErrorDetail' in str(data) and 'authentication_failed' in str(data):
                response['status'] = False
                response['message'] = 'A detailed error occurred.'
                response['status_code'] = data.get('status_code', 404)
                response['data'] = None
                response['errors'] = data.get('detail', 'A detailed error occurred.')

        
        return json.dumps(response, ensure_ascii=False)

