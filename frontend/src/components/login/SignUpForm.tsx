import React from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import '../../css/User.css';
import 'boxicons/css/boxicons.min.css';
import { useAuth } from '../../services/authContext';

type FormData = {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
};

const SignUpForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors, isSubmitting }, watch } = useForm<FormData>();
  const { registerUser } = useAuth();
  const [error, setError] = React.useState('');
  const navigate = useNavigate();
  const password = watch('password');
  

  const onSubmit = async (data: FormData) => {
    setError('');
    try {
      registerUser(data);
      navigate('/login');
    } catch (error: any) {
      setError(error.message || 'Chyba při registraci');
    }
  };

  return (
    <div className="login-container">
      <h2>Registrace</h2>
      {error && (
        <div className="error-message" style={{ color: 'red', marginTop: '10px', fontWeight: '500' }}>
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-group">
          <input type="text" placeholder="Username" {...register('name', { required: 'Zadejte uživatelské jméno' })}/>
          <i className="bx bx-user"></i>
          {errors.name && <span className="error-message">{errors.name.message}</span>}
        </div>
        <div className="form-group">
          <input type="email" placeholder="Email" {...register('email', { required: 'Zadejte email', pattern: { value: /^\S+@\S+$/i, message: 'Neplatný email'}})}/>
          <i className="bx bx-envelope"></i>
          {errors.email && <span className="error-message">{errors.email.message}</span>}
        </div>
        <div className="form-group">
          <input type="password" placeholder="Password" {...register('password', { required: 'Zadejte heslo', minLength: { value: 6, message: 'Heslo musí mít alespoň 6 znaků'}})}/>
          <i className="bx bx-lock-alt"></i>
          {errors.password && <span className="error-message">{errors.password.message}</span>}
        </div>
                <div className="form-group">
          <input 
            type="password" 
            placeholder="Confirm Password" 
            {...register('confirmPassword', { 
              required: 'Potvrďte heslo', 
              validate: value => value === password || 'Hesla se neshodují'
            })}
          />
          <i className="bx bx-lock-alt"></i>
          {errors.confirmPassword && <span className="error-message">{errors.confirmPassword.message}</span>}
        </div>
        <button type="submit" disabled={isSubmitting}>Registrovat</button>
      </form>
      <p>Máte již účet? <a href="/login">Přihlaste se</a></p>
    </div>
  );
};

export default SignUpForm;