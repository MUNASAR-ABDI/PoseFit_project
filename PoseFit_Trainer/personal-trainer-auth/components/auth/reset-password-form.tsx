"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { toast } from "@/hooks/use-toast"
import { useState } from "react"
import { useRouter } from "next/navigation"

const resetPasswordSchema = z.object({
  email: z.string().email({
    message: "Please enter a valid email address.",
  }),
  verificationCode: z.string().min(6, {
    message: "Verification code must be 6 characters.",
  }).optional(),
  newPassword: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }).optional(),
  confirmPassword: z.string().min(8, {
    message: "Password must be at least 8 characters.",
  }).optional(),
}).refine((data) => {
  if (data.verificationCode) {
    return data.newPassword === data.confirmPassword
  }
  return true
}, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type ResetPasswordValues = z.infer<typeof resetPasswordSchema>

export function ResetPasswordForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState<"request" | "verify">("request")
  const router = useRouter()

  const form = useForm<ResetPasswordValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      email: "",
      verificationCode: "",
      newPassword: "",
      confirmPassword: "",
    },
  })

  async function onSubmit(data: ResetPasswordValues) {
    try {
      setIsLoading(true)

      if (step === "request") {
        const response = await fetch("http://localhost:8005/reset-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: data.email,
          }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Failed to send reset code")
        }

        toast({
          title: "Reset code sent",
          description: "Please check your email for the verification code.",
        })

        setStep("verify")
      } else {
        const response = await fetch("http://localhost:8005/reset-password-confirm", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: data.email,
            verification_code: data.verificationCode,
            new_password: data.newPassword,
          }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Failed to reset password")
        }

        toast({
          title: "Password reset successful",
          description: "You can now log in with your new password.",
        })

        router.push("/login")
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to reset password",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input 
                  type="email" 
                  placeholder="Enter your email address" 
                  {...field}
                  disabled={step === "verify"} 
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {step === "verify" && (
          <>
            <FormField
              control={form.control}
              name="verificationCode"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Verification Code</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="Enter verification code" 
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    Enter the 6-digit code sent to your email.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="newPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>New Password</FormLabel>
                  <FormControl>
                    <Input 
                      type="password" 
                      placeholder="Enter new password" 
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    Password must be at least 8 characters long.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm New Password</FormLabel>
                  <FormControl>
                    <Input 
                      type="password" 
                      placeholder="Confirm new password" 
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </>
        )}

        <Button type="submit" disabled={isLoading}>
          {isLoading 
            ? "Processing..." 
            : step === "request" 
              ? "Send Reset Code" 
              : "Reset Password"
          }
        </Button>
      </form>
    </Form>
  )
} 