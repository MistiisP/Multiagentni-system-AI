import React from 'react';
import SignUpForm from '../components/login/SignUpForm';

const SignUp: React.FC = () => {
  return (
    <div className="signup-page" style={{ justifyContent: 'center', alignItems: 'center', marginTop: '10%' }}>
      <SignUpForm />
    </div>
  );
};

export default SignUp;