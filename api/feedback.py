from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user
from api.models import db, Feedback
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

feedback_bp = Blueprint('feedback', __name__)

class FeedbackForm(FlaskForm):
    feedback_type = SelectField('反馈类型', choices=[
        ('', '请选择反馈类型'),
        ('bug', '问题反馈'),
        ('suggestion', '建议'),
        ('complaint', '投诉'),
        ('other', '其他')
    ], validators=[DataRequired()])
    content = TextAreaField('反馈内容', validators=[DataRequired(), Length(min=10, max=500)])
    contact = StringField('联系方式')
    submit = SubmitField('提交反馈')

@feedback_bp.route('/', methods=['GET', 'POST'])
@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def get_feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            user_id=current_user.id if current_user.is_authenticated else None,
            feedback_type=form.feedback_type.data,
            content=form.content.data,
            contact=form.contact.data
        )
        db.session.add(feedback)
        db.session.commit()
        flash('反馈提交成功！', 'success')
        return redirect(url_for('feedback.get_feedback'))
    
    return render_template('feedback/feedback.html', form=form)