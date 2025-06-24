import React from "react";

interface User {
  id: number;
  name: string;
}

interface UsersDropdownProps {
  id: string;
  users: User[];
}

const UsersDropdown: React.FC<UsersDropdownProps> = ({ id, users }) => {
  return (
    <div className="dropdown-container">
      <label htmlFor={id}>Users:</label>
      <select id={id} name={id}>
        {users.map((user) => {
          return <option key={user.id}  value={user.name}>{user.name}</option>
        })}
      </select>
    </div>
  )
}

export default UsersDropdown;