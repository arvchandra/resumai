import React, { useState } from "react";

import type User from "../interfaces/User";

interface UsersTableProps {
  users: User[];
  handleUserSelect: (user: User) => void;
}

type SortColumn = keyof User;
type SortDirection = "asc" | "desc";

const SortableUsersTable: React.FC<UsersTableProps> = ({ users, handleUserSelect }) => {
  const [sortColumn, setSortColumn] = useState<SortColumn>("id");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const handleColumnSort = (columnName: keyof User) => {
    if (columnName === sortColumn) {
      const newSortDirection = sortDirection === "asc" ? "desc" : "asc";
      setSortDirection(newSortDirection);
    } else {
      setSortColumn(columnName);
      setSortDirection("asc");
    }
  }

  const sortedUsers = users.sort((a, b) => {
    const a_val = a[sortColumn];
    const b_val = b[sortColumn];
    let sortDirectionToUse = sortDirection;

    // Reverse sort direction for boolean so that True values
    // show at the top for ascending sort.
    if (typeof a_val === "boolean") {
      sortDirectionToUse = sortDirection === "asc" ? "desc" : "asc";
    }

    if (a_val < b_val) {
      return (sortDirectionToUse === "asc" ? -1 : 1);
    }
    if (a_val > b_val) {
      return (sortDirectionToUse === "asc" ? 1 : -1);
    }
    return 0;
  });

  return (
    <table className="sortableTable">
      <thead>
        <tr>
          <th className="sortableColumn" onClick={() => handleColumnSort("id")}>ID</th>
          <th className="sortableColumn" onClick={() => handleColumnSort("name")}>Name</th>
          <th className="sortableColumn" onClick={() => handleColumnSort("email")}>Email</th>
          <th className="sortableColumn" onClick={() => handleColumnSort("is_admin")}>Is Admin</th>
        </tr>
      </thead>
      <tbody>
        {sortedUsers.map((user) => {
          return (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td><a href="#" onClick={() => handleUserSelect(user)}>{user.name}</a></td>
              <td>{user.email}</td>
              <td>{user.is_admin ? "Yes" : "No"}</td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}

export default SortableUsersTable;