import { useMemo, useState, useCallback, useEffect } from 'react';
import { t } from '@apache-superset/core';
import { styled } from '@apache-superset/core/ui';
import { SupersetClient } from '@superset-ui/core';
import { useListViewResource } from 'src/views/CRUD/hooks';
import SubMenu from 'src/features/home/SubMenu';
import { ListView, ListViewFilterOperator } from 'src/components';
import { useToasts } from 'src/components/MessageToasts/withToasts';
import { Icons } from '@superset-ui/core/components/Icons';
import { Tooltip } from '@superset-ui/core/components';
import { Modal, Switch } from 'antd';
import dayjs from 'dayjs';
import AIProviderModal from './AIProviderModal';

const PAGE_SIZE = 25;

const Actions = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
  color: ${({ theme }) => theme.colorText};

  & svg {
    cursor: pointer;
  }
`;

function AIProviderList() {
  const { addDangerToast, addSuccessToast } = useToasts();
  const {
    state: {
      loading,
      resourceCount: count,
      resourceCollection: data,
      bulkSelectEnabled,
    },
    fetchData,
    refreshData,
    toggleBulkSelect,
  } = useListViewResource<any>('ai_provider', t('AI Provider'), addDangerToast);

  const [providerModalOpen, setProviderModalOpen] = useState(false);
  const [currentProvider, setCurrentProvider] = useState<any>(null);
  const [aiEnabled, setAiEnabled] = useState(true);

  // Fetch AI Config
  useEffect(() => {
    SupersetClient.get({ endpoint: '/api/v1/ai_chat/config' })
      .then(({ json }) => {
        setAiEnabled(json.result.enabled ?? true);
      })
      .catch(() => {
        // Default to true if fetch fails or config missing
        setAiEnabled(true);
      });
  }, []);

  const handleToggleAi = useCallback((checked: boolean) => {
    setAiEnabled(checked);
    SupersetClient.post({
      endpoint: '/api/v1/ai_chat/config',
      jsonPayload: { enabled: checked },
    }).then(() => {
      addSuccessToast(t('AI Assistant %s', checked ? 'Enabled' : 'Disabled'));
    }).catch(async (e) => {
      let errorMsg = t('Failed to update config');
      try {
        const response = await e?.response?.json();
        if (response?.message) errorMsg += `: ${response.message}`;
        else if (e?.statusText) errorMsg += `: ${e.statusText}`;
      } catch (parseError) {
        // Fallback to generic message
      }
      addDangerToast(errorMsg);
      setAiEnabled(!checked); // Revert on error
    });
  }, [addSuccessToast, addDangerToast]);

  const handleEdit = (provider: any) => {
    setCurrentProvider(provider);
    setProviderModalOpen(true);
  };

  const handleDelete = useCallback(
    (provider: any) => {
      Modal.confirm({
        title: t('Delete AI Provider?'),
        content: t('Are you sure you want to delete this AI Provider?'),
        onOk: async () => {
          try {
            await SupersetClient.delete({
              endpoint: `/api/v1/ai_provider/${provider.id}`,
            });
            addSuccessToast(t('Deleted: %s', provider.provider));
            refreshData();
          } catch (e) {
            const errorText = await (e as any)?.response?.text();
            addDangerToast(t('Error deleting provider: %s', errorText));
          }
        },
      });
    },
    [addSuccessToast, addDangerToast, refreshData],
  );

  const columns = useMemo(
    () => [
      {
        accessor: 'provider',
        Header: t('Provider'),
        Cell: ({ row: { original } }: any) => original.provider,
      },
      {
        accessor: 'api_key',
        Header: t('API Key'),
        Cell: ({ value }: any) => (value ? '••••••••' : t('Not Set')),
        disableSortBy: true,
      },
      {
        accessor: 'model_name',
        Header: t('Model Name'),
        Cell: ({ row: { original } }: any) => original.model_name,
      },
      {
        accessor: 'is_active',
        Header: t('Is Active'),
        Cell: ({ row: { original } }: any) =>
          original.is_active ? t('Yes') : t('No'),
      },
      {
        id: 'modified',
        Header: t('Last Modified'),
        Cell: ({ row: { original } }: any) => {
          const date = original.changed_on || original.created_on;
          return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-';
        },
      },
      {
        id: 'changed_by',
        Header: t('Modified By'),
        Cell: ({ row: { original } }: any) => {
          const { first_name, last_name } = original.changed_by || {};
          return first_name || last_name
            ? `${first_name} ${last_name}`.trim()
            : '-';
        },
      },
      {
        Cell: ({ row: { original } }: any) => {
          return (
            <Actions>
              <Tooltip title={t('Edit')}>
                <span
                  role="button"
                  tabIndex={0}
                  onClick={() => handleEdit(original)}
                >
                  <Icons.EditOutlined />
                </span>
              </Tooltip>
              <Tooltip title={t('Delete')}>
                <span
                  role="button"
                  tabIndex={0}
                  onClick={() => handleDelete(original)}
                >
                  <Icons.DeleteOutlined />
                </span>
              </Tooltip>
            </Actions>
          );
        },
        Header: t('Actions'),
        id: 'actions',
        disableSortBy: true,
      },
    ],
    [handleDelete],
  );

  const filters = useMemo(
    () => [
      {
        Header: t('Provider'),
        key: 'provider',
        id: 'provider',
        input: 'search' as const,
        operator: ListViewFilterOperator.Contains,
      },
      {
        Header: t('Model Name'),
        key: 'model_name',
        id: 'model_name',
        input: 'search' as const,
        operator: ListViewFilterOperator.Contains,
      },
    ],
    [],
  );

  return (
    <>
      <SubMenu
        name={t('AI Providers')}
        additionalActions={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 'bold' }}>{t('AI Assistant')}</span>
            <Switch checked={aiEnabled} onChange={handleToggleAi} />
          </div>
        }
        buttons={[
          {
            name: t('Provider'),
            onClick: () => {
              setCurrentProvider(null);
              setProviderModalOpen(true);
            },
            buttonStyle: 'primary',
          },
        ]}
      />
      <ListView
        className="ai-provider-list-view"
        columns={columns}
        count={count}
        data={data}
        fetchData={fetchData}
        filters={filters}
        loading={loading}
        pageSize={PAGE_SIZE}
        initialSort={[{ id: 'changed_on', desc: true }]}
        refreshData={refreshData}
        addSuccessToast={addSuccessToast}
        addDangerToast={addDangerToast}
        bulkSelectEnabled={bulkSelectEnabled}
        disableBulkSelect={toggleBulkSelect}
      />
      <AIProviderModal
        show={providerModalOpen}
        onHide={() => setProviderModalOpen(false)}
        provider={currentProvider}
        onProviderSaved={refreshData}
      />
    </>
  );
}

export default AIProviderList;
