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
from endpoints.units import unit_bp


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

@app.route('/contracts')
def contracts():
    return render_template('contract.html')

@app.route('/parking_spots')
def parking_spots():
    return render_template('parking_spot.html')

@app.route('/properties')
def property():
    return render_template('property.html')

@app.route('/units')
def units():
    return render_template('unit.html')

@app.route('/appartments')
def appartments():
    return render_template('appartment.html')

# @app.route('/tenants')
# def tenants():
#     return render_template('tenant.html')




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
app.register_blueprint(unit_bp)


if __name__ == "__main__":
    app.run(debug=True)

