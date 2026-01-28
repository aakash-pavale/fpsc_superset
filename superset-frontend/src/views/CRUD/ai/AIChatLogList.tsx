import { useMemo } from 'react';
import { t } from '@apache-superset/core';
import { useListViewResource } from 'src/views/CRUD/hooks';
import SubMenu from 'src/features/home/SubMenu';
import { ListView, ListViewFilterOperator } from 'src/components';
import { useToasts } from 'src/components/MessageToasts/withToasts';
import dayjs from 'dayjs';

const PAGE_SIZE = 25;

function AIChatLogList() {
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
  } = useListViewResource<any>('ai_chat', t('AI Chat Log'), addDangerToast);

  const columns = useMemo(
    () => [
      {
        id: 'user_name',
        Header: t('User'),
        accessor: 'user_name',
        Cell: ({ row: { original } }: any) => original.user_name || '-',
      },
      {
        id: 'dashboard_title',
        Header: t('Dashboard'),
        accessor: 'dashboard_title',
        Cell: ({ row: { original } }: any) => original.dashboard_title || '-',
      },
      {
        accessor: 'prompt',
        Header: t('Prompt'),
        Cell: ({ row: { original } }: any) => {
          const val = original.prompt;
          return val && val.length > 50 ? val.substring(0, 50) + '...' : val;
        },
      },
      {
        accessor: 'response_text',
        Header: t('Response'),
        Cell: ({ row: { original } }: any) => {
          const val = original.response_text;
          return val && val.length > 50 ? val.substring(0, 50) + '...' : val;
        },
      },
      {
        accessor: 'timestamp',
        id: 'timestamp',
        Header: t('Timestamp'),
        disableSortBy: false,
        Cell: ({ row: { original } }: any) => {
          const val = original.timestamp;
          return val ? dayjs(val).format('YYYY-MM-DD HH:mm:ss') : '-';
        },
      },
    ],
    [],
  );

  const filters = useMemo(
    () => [
      {
        Header: t('User'),
        key: 'user_name',
        id: 'user_name',
        input: 'search' as const,
        operator: ListViewFilterOperator.Contains,
      },
      {
        Header: t('Dashboard'),
        key: 'dashboard_title',
        id: 'dashboard_title',
        input: 'search' as const,
        operator: ListViewFilterOperator.Contains,
      },
      {
        Header: t('Prompt'),
        key: 'prompt',
        id: 'prompt',
        input: 'search' as const,
        operator: ListViewFilterOperator.Contains,
      },
      {
        Header: t('Response'),
        key: 'response_text',
        id: 'response_text',
        input: 'search' as const,
        operator: ListViewFilterOperator.Contains,
      },
    ],
    [],
  );

  return (
    <>
      <SubMenu name={t('AI Chat Logs')} />
      <ListView
        className="ai-chat-log-list-view"
        columns={columns}
        count={count}
        data={data}
        fetchData={fetchData}
        filters={filters}
        loading={loading}
        pageSize={PAGE_SIZE}
        initialSort={[{ id: 'timestamp', desc: true }]}
        refreshData={refreshData}
        addSuccessToast={addSuccessToast}
        addDangerToast={addDangerToast}
        bulkSelectEnabled={bulkSelectEnabled}
        disableBulkSelect={toggleBulkSelect}
      />
    </>
  );
}

export default AIChatLogList;
