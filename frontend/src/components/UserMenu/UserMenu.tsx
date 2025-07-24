import { useEffect, useRef, useState } from "react";

import { useAuth } from "../../contexts/AuthContext";
import type { User } from "../../contexts/AuthContext";

import "./UserMenu.css";
import logoutIcon from "../../assets/images/logout-icon.png";

type UserMenuProps = {
  userInfo: User;
}

export default function UserMenu({ userInfo }: UserMenuProps) {
  const [menuOpen, setMenuOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const { logout } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!userInfo) {
    return null;
  }

  const userInitials = userInfo.firstName[0] + (userInfo.lastName ? userInfo.lastName[0] : '');

  return (
    <div ref={menuRef}>
      <div className="user-icon" onClick={() => setMenuOpen(!menuOpen)}>
        {userInitials}
      </div>
      {menuOpen && (
        <div className="user-dropdown-menu">
          <div className="user-info-container">
            <div className="user-icon">
              {userInitials}
            </div>
            <div className="user-name-email-container">
              <div><strong>{`${userInfo.firstName} ${userInfo.lastName}`}</strong></div>
              <div>{userInfo.email}</div>
            </div>
          </div>
          <div className="menu-item" onClick={logout}>
            <img className="icon menu-icon" src={logoutIcon} alt="logout" />Logout
          </div>
        </div>
      )
      }
    </div >
  )
}
