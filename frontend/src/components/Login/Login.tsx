import { GoogleLogin } from '@react-oauth/google';

import type { CredentialResponse } from '@react-oauth/google';

export default function Login() {
  const responseMessage = (response: CredentialResponse) => {
    console.log(response);
  };
  const errorMessage = () => {
    console.log("error");
  };
  return (
    <div>
      <h2>React Google Login</h2>
      <br />
      <br />
      <GoogleLogin ux_mode='popup' onSuccess={responseMessage} onError={errorMessage} />
    </div>
  )
}