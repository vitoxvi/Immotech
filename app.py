from flask import Flask, render_template
from entities.properties import property_bp
from entities.apartments import apartment_bp
from entities.parking_spots import parking_spot_bp
from entities.contracts import contract_bp
from entities.persons import person_bp
from entities.tenants import tenant_bp
from entities.board_members import board_member_bp
from entities.employees import employee_bp
from entities.vehicle_usage_logs import vehicle_usage_log_bp
from entities.vehicles import vehicle_bp


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

