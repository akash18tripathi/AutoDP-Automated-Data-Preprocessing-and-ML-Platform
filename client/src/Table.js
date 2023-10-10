import React from 'react';
import ReactTable from 'react-table-6';
import 'react-table-6/react-table.css';

const Table =  ({ rows }) => {
    const columns = React.useMemo(() => {
      if (rows.length > 0) {
        return Object.keys(rows[0]).map((key) => ({
          Header: key,
          accessor: key,
        }));
      }
      return [];
    }, [rows]);
  
    return <ReactTable columns={columns} data={rows} />;
  };

  export default Table;

  