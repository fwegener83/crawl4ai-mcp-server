import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  TextField,
  Box,
  Typography,
  TablePagination,
  Checkbox
} from '@mui/material';
import { visuallyHidden } from '@mui/utils';

export interface Column<T = any> {
  id: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string | number;
  minWidth?: string | number;
}

export interface DataTableProps<T = any> {
  data: T[];
  columns: Column<T>[];
  title?: string;
  loading?: boolean;
  selectable?: boolean;
  onSelectionChange?: (selected: T[]) => void;
  searchable?: boolean;
  searchPlaceholder?: string;
  pagination?: boolean;
  rowsPerPageOptions?: number[];
  defaultRowsPerPage?: number;
  emptyMessage?: string;
  dense?: boolean;
  stickyHeader?: boolean;
  maxHeight?: string | number;
  onRowClick?: (row: T, index: number) => void;
}

type Order = 'asc' | 'desc';

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  title,
  loading = false,
  selectable = false,
  onSelectionChange,
  searchable = false,
  searchPlaceholder = 'Search...',
  pagination = true,
  rowsPerPageOptions = [10, 25, 50],
  defaultRowsPerPage = 10,
  emptyMessage = 'No data available',
  dense = false,
  stickyHeader = false,
  maxHeight,
  onRowClick,
}: DataTableProps<T>) {
  const [order, setOrder] = useState<Order>('asc');
  const [orderBy, setOrderBy] = useState<string>('');
  const [selected, setSelected] = useState<T[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(defaultRowsPerPage);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    
    return data.filter((row) =>
      columns.some((column) => {
        const value = row[column.id];
        if (value == null) return false;
        return String(value).toLowerCase().includes(searchTerm.toLowerCase());
      })
    );
  }, [data, searchTerm, columns]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!orderBy) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aVal = a[orderBy];
      const bVal = b[orderBy];
      
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return order === 'desc' ? 1 : -1;
      if (bVal == null) return order === 'desc' ? -1 : 1;
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return order === 'desc' 
          ? bVal.localeCompare(aVal)
          : aVal.localeCompare(bVal);
      }
      
      if (order === 'desc') {
        return bVal < aVal ? -1 : bVal > aVal ? 1 : 0;
      }
      return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
    });
  }, [filteredData, order, orderBy]);

  // Paginate data
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;
    
    const startIndex = page * rowsPerPage;
    return sortedData.slice(startIndex, startIndex + rowsPerPage);
  }, [sortedData, page, rowsPerPage, pagination]);

  const handleRequestSort = (property: string) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = [...paginatedData];
      setSelected(newSelected);
      onSelectionChange?.(newSelected);
    } else {
      setSelected([]);
      onSelectionChange?.([]);
    }
  };

  const handleRowSelect = (row: T) => {
    const selectedIndex = selected.findIndex(item => 
      JSON.stringify(item) === JSON.stringify(row)
    );
    let newSelected: T[] = [];

    if (selectedIndex === -1) {
      newSelected = [...selected, row];
    } else {
      newSelected = selected.filter((_, index) => index !== selectedIndex);
    }

    setSelected(newSelected);
    onSelectionChange?.(newSelected);
  };

  const isSelected = (row: T) => 
    selected.some(item => JSON.stringify(item) === JSON.stringify(row));

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      {(title || searchable) && (
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          {title && <Typography variant="h6">{title}</Typography>}
          {searchable && (
            <TextField
              size="small"
              placeholder={searchPlaceholder}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{ minWidth: 200 }}
            />
          )}
        </Box>
      )}

      <TableContainer 
        component={Paper} 
        sx={{ 
          maxHeight: maxHeight,
          ...(loading && { position: 'relative' })
        }}
      >
        <Table 
          stickyHeader={stickyHeader}
          size={dense ? 'small' : 'medium'}
        >
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selected.length > 0 && selected.length < paginatedData.length}
                    checked={paginatedData.length > 0 && selected.length === paginatedData.length}
                    onChange={handleSelectAllClick}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{ 
                    width: column.width,
                    minWidth: column.minWidth 
                  }}
                  sortDirection={orderBy === column.id ? order : false}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={() => handleRequestSort(column.id)}
                    >
                      {column.label}
                      {orderBy === column.id && (
                        <Box component="span" sx={visuallyHidden}>
                          {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                        </Box>
                      )}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell 
                  colSpan={columns.length + (selectable ? 1 : 0)} 
                  align="center"
                  sx={{ py: 4 }}
                >
                  <Typography color="text.secondary">{emptyMessage}</Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, index) => {
                const isItemSelected = isSelected(row);
                return (
                  <TableRow
                    key={index}
                    hover={!!onRowClick}
                    onClick={() => onRowClick?.(row, index)}
                    selected={isItemSelected}
                    sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={isItemSelected}
                          onChange={() => handleRowSelect(row)}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </TableCell>
                    )}
                    {columns.map((column) => (
                      <TableCell
                        key={column.id}
                        align={column.align || 'left'}
                      >
                        {column.render 
                          ? column.render(row[column.id], row)
                          : row[column.id]
                        }
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {pagination && (
        <TablePagination
          rowsPerPageOptions={rowsPerPageOptions}
          component="div"
          count={sortedData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      )}
    </Box>
  );
}

export default DataTable;