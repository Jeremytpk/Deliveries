
import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';

const csvFiles = [
  { url: './dsp_directory.csv', type: 'DSP' },
  { url: './fedex_directory.csv', type: 'FedEx' }
];

function parseCsvData(csv, type) {
  return csv.data.slice(1).map(row => {
    const obj = {};
    csv.data[0].forEach((header, i) => {
      obj[header] = row[i] || '';
    });
    obj.Type = type;
    return obj;
  });
}

function getUniqueValues(data, col) {
  return Array.from(new Set(data.map(d => d[col]).filter(Boolean)));
}

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [columns, setColumns] = useState([]);
  const pageSize = 100;

  useEffect(() => {
    Promise.all(
      csvFiles.map(file =>
        fetch(file.url)
          .then(res => res.text())
          .then(text => Papa.parse(text, { header: false }))
          .then(csv => parseCsvData(csv, file.type))
      )
    ).then(results => {
      // results[0] is DSP, results[1] is FedEx
      const renameDSPName = row => {
        const newRow = { ...row };
        if ('DSP Name' in newRow) {
          newRow.Company = newRow['DSP Name'];
          delete newRow['DSP Name'];
        }
        return newRow;
      };
      const dspData = results[0].map(row => {
        const r = renameDSPName(row);
        r.Type = 'DSP';
        return r;
      });
      const fedexData = results[1].map(row => {
        const r = renameDSPName(row);
        r.Type = 'FedEx';
        return r;
      });
      const mergedFinal = [...dspData, ...fedexData];
      setData(mergedFinal);
      if (mergedFinal.length > 0) {
        // Move 'Company' and 'Type' to the start of columns
        let cols = Object.keys(mergedFinal[0]);
        // Remove 'Email' column
        cols = cols.filter(c => c !== 'Email');
        if (cols.includes('Company') && cols.includes('Type')) {
          cols = cols.filter(c => c !== 'Company' && c !== 'Type');
          cols = ['Company', 'Type', ...cols];
        }
        setColumns(cols);
      }
      setLoading(false);
    });
  }, []);

  // Search and filter logic
  let filtered = data;
  if (search) {
    filtered = filtered.filter(row =>
      columns.some(col => (row[col] || '').toLowerCase().includes(search.toLowerCase()))
    );
  }
  Object.entries(filters).forEach(([col, val]) => {
    if (val) filtered = filtered.filter(row => row[col] === val);
  });

  // Pagination logic
  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const pagedData = filtered.slice((page - 1) * pageSize, page * pageSize);

  // Filter controls
  const filterControls = columns
    .filter(col => col !== 'Street Address' && col !== 'Company')
    .map(col => (
      <span key={col}>
        <label htmlFor={col} style={{ marginRight: 4, fontWeight: 500 }}>{col}:</label>
        <select
          id={col}
          value={filters[col] || ''}
          onChange={e => {
            setFilters(f => ({ ...f, [col]: e.target.value }));
            setPage(1);
          }}
        >
          <option value="">All</option>
          {getUniqueValues(data, col).map(v => (
            <option key={v} value={v}>{v}</option>
          ))}
        </select>
      </span>
    ));

  // Pagination controls
  const pagination = (
    <div className="pagination">
      <button onClick={() => setPage(1)} disabled={page === 1}>First</button>
      <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Prev</button>
      <span>Page {page} of {totalPages}</span>
      <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</button>
      <button onClick={() => setPage(totalPages)} disabled={page === totalPages}>Last</button>
    </div>
  );

  return (
    <div>
      <h1>Delivery Directory</h1>
      <div id="controls">
        <div className="search-group">
          <label className="search-label" htmlFor="search-input">Search</label>
          <input
            id="search-input"
            type="text"
            placeholder="Search all columns..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        {columns
          .filter(col => col !== 'Street Address' && col !== 'Company')
          .map(col => (
            <div className="filter-group" key={col}>
              <label className="filter-label" htmlFor={col}>{col}</label>
              <select
                id={col}
                value={filters[col] || ''}
                onChange={e => {
                  setFilters(f => ({ ...f, [col]: e.target.value }));
                  setPage(1);
                }}
              >
                <option value="">All</option>
                {getUniqueValues(data, col).map(v => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
            </div>
          ))}
      </div>
      <div className="table-container">
        {pagination}
        {loading ? (
          <p>Loading data...</p>
        ) : pagedData.length === 0 ? (
          <p>No data available.</p>
        ) : (
          <>
            <div className="total-entries">Total entries: {filtered.length}</div>
            <table>
              <thead>
                <tr>
                  {columns.map(col => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {pagedData.map((row, i) => (
                  <tr key={i}>
                    {columns.map(col => (
                      <td key={col}>{row[col]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {pagination}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
