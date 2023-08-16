from flask import Flask, render_template

print('Starting')

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.secret_key = 'secret_key_1'
            
    from routes import upload_routes
    app.register_blueprint(upload_routes)


    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(Exception)
    def global_exception_handler(e):
        error_message = "An error occurred: " + str(e)
        return render_template('error.html', error_message=error_message)
    
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()