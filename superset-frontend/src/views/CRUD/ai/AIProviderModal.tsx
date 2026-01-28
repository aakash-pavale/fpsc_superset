import React, { FunctionComponent, useState, useEffect } from 'react';
import { t } from '@apache-superset/core';
import { styled } from '@apache-superset/core/ui';
import { SupersetClient } from '@superset-ui/core';
import { Form, Input, Select, Checkbox, Button, Modal } from 'antd';
import { useToasts } from 'src/components/MessageToasts/withToasts';

interface AIProviderModalProps {
  show: boolean;
  onHide: () => void;
  provider?: any;
  onProviderSaved: () => void;
}

const StyledForm = styled(Form)`
  .ant-form-item {
    margin-bottom: 16px;
  }
`;

const AIProviderModal: FunctionComponent<AIProviderModalProps> = ({
  show,
  onHide,
  provider,
  onProviderSaved,
}) => {
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const { addSuccessToast, addDangerToast } = useToasts();
  const isEdit = !!provider;

  useEffect(() => {
    if (show) {
      if (provider) {
        form.setFieldsValue(provider);
      } else {
        form.resetFields();
        form.setFieldsValue({ is_active: true });
      }
    }
  }, [show, provider, form]);

  const onFinish = async (values: any) => {
    setSubmitting(true);
    try {
      if (isEdit) {
        // PUT
        await SupersetClient.put({
          endpoint: `/api/v1/ai_provider/${provider.id}`,
          jsonPayload: values,
        });
        addSuccessToast(t('AI Provider updated'));
      } else {
        // POST
        await SupersetClient.post({
          endpoint: `/api/v1/ai_provider/`,
          jsonPayload: values,
        });
        addSuccessToast(t('AI Provider created'));
      }
      onProviderSaved();
      onHide();
    } catch (e) {
      console.error('Provider API Error:', e);
      const errorText =
        (await (e as any)?.response?.json())?.message ||
        (await (e as any)?.response?.text()) ||
        'Unknown Error';
      addDangerToast(t('Error saving provider: %s', errorText));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={isEdit ? t('Edit AI Provider') : t('Add AI Provider')}
      visible={show}
      onCancel={onHide}
      footer={[
        <Button key="back" onClick={onHide}>
          {t('Cancel')}
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={submitting}
          onClick={form.submit}
        >
          {t('Save')}
        </Button>,
      ]}
    >
      <StyledForm
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{ is_active: true }}
      >
        <Form.Item
          name="provider"
          label={t('Provider')}
          rules={[{ required: true, message: t('Please select a provider') }]}
        >
          <Select>
            <Select.Option value="openai">OpenAI</Select.Option>
            <Select.Option value="gemini">Google Gemini</Select.Option>
            <Select.Option value="deepseek">DeepSeek</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="api_key"
          label={t('API Key')}
          rules={[{ required: true, message: t('Please enter API Key') }]}
        >
          <Input.Password placeholder="sk-..." />
        </Form.Item>

        <Form.Item
          name="model_name"
          label={t('Model Name')}
          rules={[{ required: true, message: t('Please enter Model Name') }]}
        >
          <Input placeholder="e.g. gpt-4o, gemini-pro" />
        </Form.Item>

        <Form.Item name="is_active" valuePropName="checked">
          <Checkbox>{t('Is Active')}</Checkbox>
        </Form.Item>
      </StyledForm>
    </Modal>
  );
};

export default AIProviderModal;
