export type Customer = {
  id: string;
  tenant_id: string;
  name: string;
  email: string;
};

export type SaveFailure = {
  kind: "error" | "unconfirmed" | "unauthenticated" | "forbidden";
  message: string;
};

export function saveFailure(status: number | null): SaveFailure {
  switch (status) {
    case 400:
      return {
        kind: "error",
        message: "Check the name and email, then try again.",
      };
    case 401:
      return {
        kind: "unauthenticated",
        message: "Your session has ended. Return to the host application.",
      };
    case 403:
      return {
        kind: "forbidden",
        message: "You do not have permission to add customers.",
      };
    case 409:
      return {
        kind: "error",
        message: "A customer with this email already exists.",
      };
    case 413:
      return { kind: "error", message: "The customer details are too long." };
    default:
      return {
        kind: "unconfirmed",
        message:
          "We could not confirm whether the customer was saved. Check the customer list before taking further action.",
      };
  }
}

export function isCustomer(value: unknown): value is Customer {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    typeof value.id === "string" &&
    "tenant_id" in value &&
    typeof value.tenant_id === "string" &&
    "name" in value &&
    typeof value.name === "string" &&
    "email" in value &&
    typeof value.email === "string"
  );
}

export async function sessionTenant(signal: AbortSignal): Promise<string> {
  const response = await fetch("/session", { signal, cache: "no-store" });
  if (!response.ok) throw new Error("Session unavailable");
  const session: unknown = await response.json();
  if (
    typeof session !== "object" ||
    !session ||
    !("tenant_id" in session) ||
    typeof session.tenant_id !== "string"
  ) {
    throw new Error("Invalid session");
  }
  return session.tenant_id;
}
