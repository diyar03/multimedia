import waitress
import Back_Pain_App

waitress.serve(Back_Pain_App.app, host='0.0.0.0', port=40000)
