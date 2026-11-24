/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Controller, type Control } from "react-hook-form";

interface InputFieldProps {
  control: Control<any>;
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  min?: number;
}

export default function InputField({
  control,
  name,
  label,
  placeholder,
  className,
  disabled,
  type,
  min,
}: InputFieldProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid} className={className}>
          <FieldLabel>{label}</FieldLabel>
          <Input
            {...field}
            placeholder={placeholder}
            disabled={disabled}
            type={type}
            min={min}
            aria-invalid={fieldState.invalid}
          />
          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  );
}
