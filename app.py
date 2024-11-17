from flask import Flask, render_template
from endpoints.properties import property_bp
from endpoints.apartments import apartment_bp
from endpoints.parking_spots import parking_spot_bp
from endpoints.contracts import contract_bp
from endpoints.persons import person_bp
from endpoints.tenants import tenant_bp
from endpoints.board_members import board_member_bp
from endpoints.employees import employee_bp
from endpoints.vehicle_usage_logs import vehicle_usage_log_bp
from endpoints.vehicles import vehicle_bp


app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/vehicles')
def vehicles():
    return render_template('vehicle.html')

@app.route('/employees')
def employees():
    return render_template('employee.html')

@app.route('/boardmembers')
def boardmembers():
    return render_template('board_member.html')

@app.route('/vehicle-usage-logs')
def vehicle_usage_logs():
    return render_template('vehicle_usage_log.html')


# Register Blueprints
app.register_blueprint(property_bp)
app.register_blueprint(apartment_bp)
app.register_blueprint(parking_spot_bp)
app.register_blueprint(contract_bp)
app.register_blueprint(person_bp)
app.register_blueprint(tenant_bp)
app.register_blueprint(board_member_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(vehicle_usage_log_bp)
app.register_blueprint(vehicle_bp)

if __name__ == "__main__":
    app.run(debug=True)

