import UserMenu from "../UserMenu/UserMenu";

import { useAuth } from "../../contexts/AuthContext";

import "./Header.css";

export default function Header() {
  const { userInfo } = useAuth();

  return (
    <div className="header">
      <div style={{width: "35px"}}></div>
      <div className="header-title">ResumAI</div>
      {userInfo && <UserMenu userInfo={userInfo} />}
    </div>
  )
}
