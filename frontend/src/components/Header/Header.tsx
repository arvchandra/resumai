import UserMenu from "../UserMenu/UserMenu";

import "./Header.css";

export default function Header() {

  return (
    <div className="header">
      <div>ResumAI Logo</div>
      <UserMenu />
    </div>
  )
}
