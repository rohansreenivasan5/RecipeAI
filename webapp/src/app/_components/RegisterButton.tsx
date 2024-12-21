"use client";

import { useFormStatus } from "react-dom";

export const RegisterButton = () => {
  const { pending } = useFormStatus();
  if (pending) {
    return (
      <button
        disabled
        className="w-full bg-gray-400 p-3 text-center text-white rounded font-semibold"
      >
        Loading...
      </button>
    );
  }
  return (
    <button className="w-full bg-black p-3 text-center text-white rounded font-semibold">
      Register
    </button>
  );
};
