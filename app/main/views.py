from flask import render_template, url_for, redirect, abort, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.main import main
from app.models import User, Facility, RepairPersons, Repairs, RepairStatus 

from app.main.forms import (
   AddFacilityDetailsForm, AddRepairPersons, RepairDetailsForm, RequestRepairForm, RejectRepairForm
)

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    repairs = []
    if current_user.is_admin:
        repairs = Repairs.query.order_by(Repairs.date_requested.desc()).all()
        
        form = AddFacilityDetailsForm()
        return render_template('main/add_facility.html', form=form)
    else:
        repairs = Repairs.query.filter_by(
            requested_by_id=current_user.id).order_by(Repairs.date_requested.desc())
    
        form = RequestRepairForm()
        return render_template('main/request_repair.html', form=form)


@main.route('/add-facility', methods=['GET','POST'])
def add_facility():
    form = AddFacilityDetailsForm()
    if form.validate_on_submit():
        facility = Facility( 
                facility_name= form.facility_name.data,
                facility_description = form.facility_description.data
                
             
        )
        db.session.add(facility)
        db.session.commit()
        flash('You have added a facility')
        return redirect(url_for('main.add_facility'))
    return render_template('main/add_facility.html', form=form)
 
      
        
@main.route('/add_repair_persons', methods=['GET','POST'])
@login_required
def add_maintainer():
    form = AddRepairPersons()
    if form.validate_on_submit():
        repairPerson = RepairPersons( 
                name= form.name.data,
                phone_no = form.phone_no.data
                
             
        )
        db.session.add(repairPerson)
        db.session.commit()
        flash('You have added a maintainer')
        return redirect(url_for('main.add_maintainer'))
    return render_template('main/add_maintainer.html', form=form)




@main.route('/request-repair', methods=['GET', 'POST'])
@login_required
def request_repair():
    form = RequestRepairForm()
    if form.validate_on_submit():
        repair = Repairs(
            requested_by_id=current_user.id,
            facility_id=form.facility.data,
            description=form.description.data,
            
        )
        db.session.add(repair)
        db.session.commit()     
        #Notify admin
        
        #return redirect(url_for('main.view_request_progress', repair_id=repair.id))
        flash('Great you made a request')
        return redirect(url_for('main.request_repair'))
    return render_template('main/request_repair.html', form=form)


       
@main.route('/view-repairs/<int:repair_id>')
@login_required
def view_repairs(repair_id):
    repair = Repairs.query.get_or_404(repair_id)
    if not (current_user.is_admin):
        if Repairs.requested_by_id != current_user.id:
            abort(403)
    return render_template('main/repair_detail.html', repair=repair)


       
   
@main.route('/new-requests')
@login_required
def view_new_requests():
    if current_user.is_admin:
        r = Repairs.query.order_by(Repairs.date_requested.desc()).all()
    
    
    return render_template('main/new_requests.html', r=r)

@main.route('/repairs/reject/<int:repairs_id>', methods=['GET', 'POST', 'DELET'])
@login_required
def reject_repair_request(repairs_id):
    # import pdb; pdb.set_trace()
    if not current_user.is_admin:
        abort(403)
    repair = Repairs.query.get_or_404(repairs_id)
    form = RejectRepairForm()

    if request.method == 'GET':
        temp = {
            'description': repair.description,
            'date_requested': repair.date_requested,
            'facility': repair.facility,
            'requested_by': repair.requested_by.email,
            'requested_by_name': repair.requested_by.username,
            'reasons': form.reasons.data
        }
        db.session.delete(repair)
        db.session.commit()



        #send_mail(repair=temp, rejected=True)
        return redirect(url_for('main.view_new_requests'))
    # if request.method == "DELETE":
    #     print "fdgrfgf"
    return render_template('main/new_requests.html', repair=repair, form=form)




@main.route('/request-progress')
@login_required
def view_request_progress():
    if current_user.is_admin:
        rep = Repairs.query.order_by(Repairs.date_requested.desc()).all()
        #traq = RepairPersons.query.filter_by(repairpersons.id = repairPersons.)
  
    
    return render_template('main/request_progress.html', rep=rep)


   