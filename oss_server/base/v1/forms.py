from django import forms
from django.core.exceptions import ValidationError

from oss_server.fields import AddressField, ColorField, MintAmountField, TxAmountField


class CreateLicenseRawTxForm(forms.Form):
    alliance_member_address = AddressField(error_messages={
        'required': '`alliance_member_address` is required',
        'invalid': '`alliance_member_address` is not an address'
    })
    to_address = AddressField(error_messages={
        'required': '`to_address` is required',
        'invalid': '`to_address` is not an address'
    })
    color_id = ColorField(error_messages={
        'required': '`color_id` is required',
        'invalid': '`color_id` is invalid',
        'min_value': '`color_id` should be greater than or equal to %(limit_value)s',
        'max_value': '`color_id` should be less than or equal to %(limit_value)s'
    })
    name = forms.CharField(max_length=32,
                           error_messages={
                               'required': '`name` is required',
                               'max_length': 'length of `name` should not exceed 32'
                           })
    description = forms.CharField(max_length=40,
                                  error_messages={
                                      'required': '`description` is required',
                                      'max_length': 'length of `description` should not exceed 40'
                                  })
    metadata_link = forms.CharField(max_length=100,
                                    error_messages={
                                        'required': '`metadata_link` is required',
                                        'max_length': 'length of `metadata_link` should not exceed 100'
                                    })
    member_control = forms.BooleanField(required=False)
    upper_limit = forms.IntegerField(max_value=10**10, min_value=0, required=False,
                                     error_messages={
                                         'min_value': '`upper_limit` should be greater than or equal to %(limit_value)s',
                                         'max_value': '`upper_limit` should be less than or equal to %(limit_value)s'
                                     })


class CreateSmartContractRawTxForm(forms.Form):
    address = AddressField(error_messages={
        'required': '`address` is required',
        'invalid': '`address` is not an address'
    })
    oracles_multisig_address = AddressField(error_messages={
        'required': '`oracles_multisig_address` is required',
        'invalid': '`oracles_multisig_address` is not an address'
    })
    code = forms.CharField(max_length=128000,
                           error_messages={
                               'required': '`code` is required',
                               'max_length': 'length of `code` should not exceed %(limit_value)s'
                           })
    contract_fee = forms.IntegerField(max_value=10**10, min_value=1, required=False,
                                      error_messages={
                                          'min_value': '`contract_fee` should be greater than or equal to %(limit_value)s',
                                          'max_value': '`contract_fee` should be less than or equal to %(limit_value)s'
                                      })


class RawTxForm(forms.Form):
    from_address = AddressField(error_messages={
        'required': '`from_address` is required',
        'invalid': '`from_address` is not an address'
    })
    to_address = AddressField(error_messages={
        'required': '`to_address` is required',
        'invalid': '`to_address` is not an address'
    })
    color_id = ColorField(error_messages={
        'required': '`color_id` is required',
        'invalid': '`color_id` is invalid',
        'min_value': '`color_id` should be greater than or equal to %(limit_value)s',
        'max_value': '`color_id` should be less than or equal to %(limit_value)s'
    })
    amount = TxAmountField(error_messages={
        'required': '`amount` is required',
        'invalid': '`amount` is invalid',
        'min_value': '`amount` should be greater than or equal to %(limit_value)s',
        'max_value': '`amount` should be less than or equal to %(limit_value)s',
        'max_decimal_places': '`amount` only allow up to %(max)s decimal digits'
    })


class MintRawTxForm(forms.Form):
    mint_address = AddressField(error_messages={
        'required': '`mint_address` is required',
        'invalid': '`mint_address` is not an address'
    })
    color_id = ColorField(error_messages={
        'required': '`color_id` is required',
        'invalid': '`color_id` is invalid',
        'min_value': '`color_id` should be greater than or equal to %(limit_value)s',
        'max_value': '`color_id` should be less than or equal to %(limit_value)s'
    })
    amount = MintAmountField(error_messages={
        'required': '`amount` is required',
        'invalid': '`amount` is invalid',
        'min_value': '`amount` should be greater than or equal to %(limit_value)s',
        'max_value': '`amount` should be less than or equal to %(limit_value)s',
    })

    def clean(self):
        cleaned_data = super(MintRawTxForm, self).clean()
        color_id = cleaned_data.get('color_id')
        amount = cleaned_data.get('amount')

        if color_id == 0 and amount and amount != 1:
            raise ValidationError('can only mint 1 `color 0` at one time', code='invalid')


class CreateLicenseTransferRawTxForm(forms.Form):
    from_address = AddressField(error_messages={
        'required': '`from_address` is required',
        'invalid': '`from_address` is not an address'
    })
    to_address = AddressField(error_messages={
        'required': '`to_address` is required',
        'invalid': '`to_address` is not an address'
    })
    color_id = ColorField(error_messages={
        'required': '`color_id` is required',
        'invalid': '`color_id` is invalid',
        'min_value': '`color_id` should be greater than or equal to %(limit_value)s',
        'max_value': '`color_id` should be less than or equal to %(limit_value)s'
    })


class ExchangeRawTxForm(forms.Form):
    fee_address = AddressField(error_messages={
        'required': '`fee_address` is required',
        'invalid': '`fee_address` is not an address'
    })
    address1 = AddressField(error_messages={
        'required': '`address1` is required',
        'invalid': '`address1` is not an address'
    })
    address2 = AddressField(error_messages={
        'required': '`address2` is required',
        'invalid': '`address2` is not an address'
    })
    color_id1 = ColorField(error_messages={
        'required': '`color_id1` is required',
        'invalid': '`color_id1` is invalid',
        'min_value': '`color_id1` should be greater than or equal to %(limit_value)s',
        'max_value': '`color_id1` should be less than or equal to %(limit_value)s'
    })
    color_id2 = ColorField(error_messages={
        'required': '`color_id2` is required',
        'invalid': '`color_id2` is invalid',
        'min_value': '`color_id2` should be greater than or equal to %(limit_value)s',
        'max_value': '`color_id2` should be less than or equal to %(limit_value)s'
    })
    amount1 = TxAmountField(error_messages={
        'required': '`amount1` is required',
        'invalid': '`amount1` is invalid',
        'min_value': '`amount1` should be greater than or equal to %(limit_value)s',
        'max_value': '`amount1` should be less than or equal to %(limit_value)s',
        'max_decimal_places': '`amount1` only allow up to %(max)s decimal digits'
    })
    amount2 = TxAmountField(error_messages={
        'required': '`amount2` is required',
        'invalid': '`amount2` is invalid',
        'min_value': '`amount2` should be greater than or equal to %(limit_value)s',
        'max_value': '`amount2` should be less than or equal to %(limit_value)s',
        'max_decimal_places': '`amount2` only allow up to %(max)s decimal digits'
    })

    def clean(self):
        address1 = self.cleaned_data.get('address1')
        address2 = self.cleaned_data.get('address2')

        if address1 and address2:
            if address1 == address2:
                raise forms.ValidationError("`address1` and `address2` can't be the same")
