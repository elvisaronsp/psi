# coding=utf-8
from datetime import datetime
from functools import partial

from app import service, const
from app.models import EnumValues
from app.services.sales_order import SalesOrderService
from app.utils import current_user, form_util
from app.views.components import ReadonlyStringField, DisabledStringField
from flask_admin.model.template import BaseListRowAction
from flask_admin.contrib.sqla.filters import FloatGreaterFilter, FloatSmallerFilter, FloatEqualFilter
from flask_admin.model import InlineFormAdmin
from flask_babelex import lazy_gettext
from markupsafe import Markup

from app.views.base import ModelViewWithAccess


class MarkInvalidRowAction(BaseListRowAction):
    def __init__(self, icon_class, title=None, id_arg='id', url_args=None):
        super(MarkInvalidRowAction, self).__init__(title=title)

        self.icon_class = icon_class
        self.id_arg = id_arg
        self.url_args = url_args

    def render(self, context, row_id, row):
        kwargs = dict(self.url_args) if self.url_args else {}
        kwargs[self.id_arg] = row_id
        so_invalid_status = EnumValues.find_one_by_code(const.SO_INVALID_STATUS_KEY)
        if row.status.code == const.SO_CREATED_STATUS_KEY and row.type.code == const.FRANCHISE_SO_TYPE_KEY:
            return Markup("""<a class='icon' href='javascript:MarkInvalidRowAction({0}, {1})'>
                               <span id='mark_invalid_row_action_{0}' class='fa fa-minus-circle'></span>
                            </a>""".format(row_id, so_invalid_status.id))
        else:
            return ''


class MarkShipRowAction(BaseListRowAction):
    def __init__(self, icon_class, title=None, id_arg='id', url_args=None):
        super(MarkShipRowAction, self).__init__(title=title)

        self.icon_class = icon_class
        self.id_arg = id_arg
        self.url_args = url_args

    def render(self, context, row_id, row):
        kwargs = dict(self.url_args) if self.url_args else {}
        kwargs[self.id_arg] = row_id
        so_shipped_status = EnumValues.find_one_by_code(const.SO_SHIPPED_STATUS_KEY)
        if row.status.code == const.SO_CREATED_STATUS_KEY and row.type.code == const.FRANCHISE_SO_TYPE_KEY:
            return Markup("""<a class='icon' href='javascript:MarkShipRowAction({0}, {1})'>
                               <span id='mark_ship_row_action_{0}' class='fa fa-truck'></span>
                            </a>""".format(row_id, so_shipped_status.id))
        else:
            return ''


class SalesOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.retail_price = DisabledStringField(label=lazy_gettext('Retail Price'))
        form.price_discount = DisabledStringField(label=lazy_gettext('Price Discount'))
        form.original_amount = DisabledStringField(label=lazy_gettext('Original Amount'))
        form.actual_amount = DisabledStringField(label=lazy_gettext('Actual Amount'))
        form.discount_amount = DisabledStringField(label=lazy_gettext('Discount Amount'))
        form.remark = None
        form.sol_shipping_line = None
        form.external_id = None
        return form


class SalesOrderAdmin(ModelViewWithAccess):
    from app.models import SalesOrderLine, SalesOrder
    from formatter import expenses_formatter, incoming_formatter, shipping_formatter, default_date_formatter

    column_extra_row_actions = [
        MarkShipRowAction('fa fa-camera-retro'),
        MarkInvalidRowAction('fa fa-minus-circle')
    ]

    column_list = ('id', 'type', 'status', 'customer', 'logistic_amount', 'actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'so_shipping', 'remark')
    column_filters = ('order_date', 'logistic_amount',
                      FloatSmallerFilter(SalesOrder.actual_amount, lazy_gettext('Actual Amount')),
                      FloatGreaterFilter(SalesOrder.actual_amount, lazy_gettext('Actual Amount')),
                      FloatEqualFilter(SalesOrder.actual_amount, lazy_gettext('Actual Amount')),
                      FloatSmallerFilter(SalesOrder.discount_amount, lazy_gettext('Discount Amount')),
                      FloatGreaterFilter(SalesOrder.discount_amount, lazy_gettext('Discount Amount')),
                      FloatEqualFilter(SalesOrder.discount_amount, lazy_gettext('Discount Amount')),
                      FloatSmallerFilter(SalesOrder.original_amount, lazy_gettext('Total Amount')),
                      FloatGreaterFilter(SalesOrder.original_amount, lazy_gettext('Total Amount')),
                      FloatEqualFilter(SalesOrder.original_amount, lazy_gettext('Total Amount')),)

    column_searchable_list = ('customer.first_name', 'customer.last_name', 'remark', 'type.display', 'type.code',
                              'status.display', 'status.code', 'customer.mobile_phone', 'customer.email',
                              'customer.address', 'customer.level.display', 'customer.join_channel.display')

    form_columns = ('id', 'customer', 'logistic_amount', 'order_date', 'remark', 'actual_amount',
                    'original_amount', 'discount_amount', 'lines')
    form_edit_rules = ('customer', 'logistic_amount', 'order_date', 'remark', 'actual_amount',
                       'original_amount', 'discount_amount', 'lines')
    form_create_rules = ('customer', 'logistic_amount', 'order_date', 'remark', 'lines',)

    column_details_list = ('id', 'type', 'status', 'customer', 'external_id', 'logistic_amount', 'order_date', 'remark',
                           'actual_amount', 'original_amount', 'discount_amount', 'incoming', 'expense',
                           'so_shipping', 'lines',)

    column_editable_list = ('remark',)

    form_extra_fields = {
        'transient_external_id': DisabledStringField(label=lazy_gettext('External Id')),
        'actual_amount': DisabledStringField(label=lazy_gettext('Actual Amount')),
        'original_amount': DisabledStringField(label=lazy_gettext('Original Amount')),
        'discount_amount': DisabledStringField(label=lazy_gettext('Discount Amount'))
    }

    form_overrides = dict(external_id=ReadonlyStringField)

    form_args = dict(
        logistic_amount=dict(default=0),
        order_date=dict(default=datetime.now())
    )
    form_excluded_columns = ('incoming', 'expense', 'so_shipping')
    column_sortable_list = ('id', 'logistic_amount', 'actual_amount', 'original_amount', 'discount_amount',
                            'order_date',('status', 'status.display'), ('type', 'type.display'))

    inline_models = (SalesOrderLineInlineAdmin(SalesOrderLine),)

    column_formatters = {
        'expense': expenses_formatter,
        'incoming': incoming_formatter,
        'so_shipping': shipping_formatter,
        'order_date': default_date_formatter,
    }

    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'remark': lazy_gettext('Remark'),
        'actual_amount': lazy_gettext('Actual Amount'),
        'original_amount': lazy_gettext('Original Amount'),
        'discount_amount': lazy_gettext('Discount Amount'),
        'incoming': lazy_gettext('Related Incoming'),
        'expense': lazy_gettext('Related Expense'),
        'so_shipping': lazy_gettext('Related Shipping'),
        'lines': lazy_gettext('Lines'),
        'external_id': lazy_gettext('External Id'),
        'customer': lazy_gettext('Customer'),
        'customer.name': lazy_gettext('Customer'),
        'status': lazy_gettext('Status'),
        'type': lazy_gettext('Type'),
    }

    def create_form(self, obj=None):
        from app.models import Customer

        form = super(SalesOrderAdmin, self).create_form(obj)
        form.lines.form.actual_amount = None
        form.lines.form.discount_amount = None
        form.lines.form.original_amount = None
        form.lines.form.price_discount = None
        form.lines.form.retail_price = None
        form_util.filter_by_organization(form.customer, Customer)
        self.filter_product(form)
        return form

    def edit_form(self, obj=None):
        from app.models import Customer

        form = super(SalesOrderAdmin, self).edit_form(obj)
        form_util.filter_by_organization(form.customer, Customer)
        self.filter_product(form)
        return form

    @staticmethod
    def filter_product(form):
        # Set query factory for new created line
        from app.models import Product

        form.lines.form.product.kwargs['query_factory'] = partial(Product.organization_filter, current_user.organization_id)
        # Set query object filter for existing lines
        line_entries = form.lines.entries
        for sub_line in line_entries:
            form_util.filter_by_organization(sub_line.form.product, Product)

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.type = EnumValues.find_one_by_code(const.DIRECT_SO_TYPE_KEY)
            model.status = EnumValues.find_one_by_code(const.SO_DELIVERED_STATUS_KEY)
            model.organization = current_user.organization

    def after_model_change(self, form, model, is_created):
        incoming = SalesOrderService.create_or_update_incoming(model)
        expense = SalesOrderService.create_or_update_expense(model)
        shipping = None
        if model.type.code == const.DIRECT_SO_TYPE_KEY:
            shipping = SalesOrderService.create_or_update_shipping(model)
        db = service.Info.get_db()
        if expense is not None:
            db.session.add(expense)
        if incoming is not None:
            db.session.add(incoming)
        if shipping is not None:
            db.session.add(shipping)
        db.session.commit()

    @property
    def role_identify(self):
        return "direct_sales_order"
