# 📅 Day 16 – Forms

## 🎯 Learning Goals
- Master React Hook Form
- Learn Formik basics
- Validate with Zod
- Compare form library approaches

---

## 📚 Theory

### React Hook Form

```tsx
import { useForm, Controller, SubmitHandler } from 'react-hook-form';

// Basic usage
interface LoginForm {
  email: string;
  password: string;
  rememberMe: boolean;
}

function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue,
  } = useForm<LoginForm>({
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit: SubmitHandler<LoginForm> = async (data) => {
    console.log(data);
    // API call
    reset();
  };

  // Watch a field
  const watchEmail = watch('email');

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: 'Invalid email address',
          },
        })}
        placeholder="Email"
      />
      {errors.email && <span>{errors.email.message}</span>}

      <input
        type="password"
        {...register('password', {
          required: 'Password is required',
          minLength: {
            value: 8,
            message: 'Password must be at least 8 characters',
          },
        })}
        placeholder="Password"
      />
      {errors.password && <span>{errors.password.message}</span>}

      <label>
        <input type="checkbox" {...register('rememberMe')} />
        Remember me
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
}

// With Controller for custom components
function FormWithController() {
  const { control, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(console.log)}>
      <Controller
        name="select"
        control={control}
        rules={{ required: true }}
        render={({ field, fieldState: { error } }) => (
          <>
            <Select {...field} options={options} />
            {error && <span>This field is required</span>}
          </>
        )}
      />
    </form>
  );
}
```

### Zod Validation

```tsx
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

// Define schema
const userSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain number'),
  confirmPassword: z.string(),
  age: z.number().min(18, 'Must be 18+').optional(),
  website: z.string().url().optional().or(z.literal('')),
  role: z.enum(['admin', 'user', 'guest']),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

// Infer type from schema
type UserFormData = z.infer<typeof userSchema>;

function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      role: 'user',
    },
  });

  const onSubmit = (data: UserFormData) => {
    console.log('Valid data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} placeholder="Name" />
      {errors.name && <span>{errors.name.message}</span>}

      <input {...register('email')} placeholder="Email" />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register('password')} placeholder="Password" />
      {errors.password && <span>{errors.password.message}</span>}

      <input
        type="password"
        {...register('confirmPassword')}
        placeholder="Confirm Password"
      />
      {errors.confirmPassword && <span>{errors.confirmPassword.message}</span>}

      <input
        type="number"
        {...register('age', { valueAsNumber: true })}
        placeholder="Age"
      />
      {errors.age && <span>{errors.age.message}</span>}

      <select {...register('role')}>
        <option value="user">User</option>
        <option value="admin">Admin</option>
        <option value="guest">Guest</option>
      </select>

      <button type="submit">Submit</button>
    </form>
  );
}
```

### Advanced Zod Patterns

```tsx
// Conditional validation
const formSchema = z.discriminatedUnion('accountType', [
  z.object({
    accountType: z.literal('personal'),
    name: z.string(),
    age: z.number().min(18),
  }),
  z.object({
    accountType: z.literal('business'),
    companyName: z.string(),
    taxId: z.string(),
  }),
]);

// Transform data
const transformSchema = z.object({
  email: z.string().email().toLowerCase(),
  name: z.string().trim().transform(s => s.toUpperCase()),
  birthDate: z.string().transform(s => new Date(s)),
});

// Custom validation
const passwordSchema = z.string().refine(
  (val) => /[A-Z]/.test(val) && /[0-9]/.test(val),
  'Password must contain uppercase and number'
);

// Async validation
const usernameSchema = z.string().refine(
  async (username) => {
    const exists = await checkUsernameExists(username);
    return !exists;
  },
  'Username already taken'
);
```

### Formik

```tsx
import { Formik, Form, Field, ErrorMessage, useFormik } from 'formik';
import * as Yup from 'yup';

// With Formik component
const validationSchema = Yup.object({
  email: Yup.string().email('Invalid email').required('Required'),
  password: Yup.string().min(8, 'Too short').required('Required'),
});

function LoginFormik() {
  return (
    <Formik
      initialValues={{ email: '', password: '' }}
      validationSchema={validationSchema}
      onSubmit={(values, { setSubmitting, resetForm }) => {
        setTimeout(() => {
          console.log(values);
          setSubmitting(false);
          resetForm();
        }, 1000);
      }}
    >
      {({ isSubmitting, touched, errors }) => (
        <Form>
          <Field type="email" name="email" placeholder="Email" />
          <ErrorMessage name="email" component="span" className="error" />

          <Field type="password" name="password" placeholder="Password" />
          <ErrorMessage name="password" component="span" />

          <button type="submit" disabled={isSubmitting}>
            Submit
          </button>
        </Form>
      )}
    </Formik>
  );
}

// With useFormik hook
function UseFormikExample() {
  const formik = useFormik({
    initialValues: { email: '', password: '' },
    validationSchema,
    onSubmit: (values) => {
      console.log(values);
    },
  });

  return (
    <form onSubmit={formik.handleSubmit}>
      <input
        name="email"
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        value={formik.values.email}
      />
      {formik.touched.email && formik.errors.email && (
        <span>{formik.errors.email}</span>
      )}
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Comparison

```tsx
// React Hook Form vs Formik

// ✅ React Hook Form
// - Uncontrolled inputs (better performance)
// - Minimal re-renders
// - Smaller bundle size (~9kb)
// - TypeScript first
// - Works with Zod (modern)

// ✅ Formik
// - Controlled inputs
// - More mature ecosystem
// - Works well with Yup
// - Easier mental model for beginners
// - More explicit state management

// 2026 Recommendation: React Hook Form + Zod
// - Better performance
// - Type safety
// - Modern tooling
```

---

## ✅ Task: Multi-Step Form with Validation

```tsx
import { useForm, useFormContext, FormProvider } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

// Step schemas
const step1Schema = z.object({
  firstName: z.string().min(2),
  lastName: z.string().min(2),
  email: z.string().email(),
});

const step2Schema = z.object({
  address: z.string().min(5),
  city: z.string().min(2),
  zipCode: z.string().regex(/^\d{5}$/),
});

const step3Schema = z.object({
  cardNumber: z.string().regex(/^\d{16}$/),
  expiryDate: z.string().regex(/^\d{2}\/\d{2}$/),
  cvv: z.string().regex(/^\d{3}$/),
});

const fullSchema = step1Schema.merge(step2Schema).merge(step3Schema);
type FormData = z.infer<typeof fullSchema>;

function MultiStepForm() {
  const [step, setStep] = useState(1);
  const methods = useForm<FormData>({
    resolver: zodResolver(fullSchema),
    mode: 'onChange',
  });

  const schemas = [step1Schema, step2Schema, step3Schema];

  const nextStep = async () => {
    const currentSchema = schemas[step - 1];
    const fields = Object.keys(currentSchema.shape) as (keyof FormData)[];
    const isValid = await methods.trigger(fields);
    if (isValid) setStep(s => Math.min(s + 1, 3));
  };

  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const onSubmit = (data: FormData) => {
    console.log('Complete form data:', data);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <StepIndicator currentStep={step} totalSteps={3} />
        
        {step === 1 && <Step1 />}
        {step === 2 && <Step2 />}
        {step === 3 && <Step3 />}

        <div className="buttons">
          {step > 1 && <button type="button" onClick={prevStep}>Back</button>}
          {step < 3 ? (
            <button type="button" onClick={nextStep}>Next</button>
          ) : (
            <button type="submit">Submit</button>
          )}
        </div>
      </form>
    </FormProvider>
  );
}

function Step1() {
  const { register, formState: { errors } } = useFormContext<FormData>();
  return (
    <div>
      <h2>Personal Info</h2>
      <input {...register('firstName')} placeholder="First Name" />
      {errors.firstName && <span>{errors.firstName.message}</span>}
      
      <input {...register('lastName')} placeholder="Last Name" />
      {errors.lastName && <span>{errors.lastName.message}</span>}
      
      <input {...register('email')} placeholder="Email" />
      {errors.email && <span>{errors.email.message}</span>}
    </div>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: Why use React Hook Form over controlled inputs?
**Answer:** RHF uses uncontrolled inputs (refs), avoiding re-renders on every keystroke. Better performance for large forms. Only validates/re-renders on submit or blur.

### Q2: What is Zod and why use it?
**Answer:** Zod is a TypeScript-first schema validation library. Benefits: type inference (`z.infer`), runtime validation, composable schemas, great DX. Preferred over Yup in 2026 for type safety.

### Q3: How do you handle multi-step form validation?
**Answer:** Use `FormProvider` to share form context, validate per-step with `trigger()` for specific fields, merge schemas for final validation. Maintain single form state across steps.

---

## ✅ Completion Checklist

- [ ] Can use React Hook Form
- [ ] Understand Zod validation
- [ ] Know Formik basics
- [ ] Built multi-step form
- [ ] Can compare form libraries

---

**Previous:** [Day 15 - TypeScript](../day-15/README.md)  
**Next:** [Day 17 - API Layer](../day-17/README.md)
