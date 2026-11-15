import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type MouseEvent,
} from "react";
import {
  isCustomer,
  saveFailure,
  sessionTenant,
  type Customer,
  type SaveFailure,
} from "./api";

const listPath = "/customers";
const createPath = "/customers/new";
type Navigate = (path: string) => void;

function RouteLink({
  path,
  navigate,
  children,
  className,
}: {
  path: string;
  navigate: Navigate;
  children: string;
  className?: string;
}) {
  function follow(event: MouseEvent<HTMLAnchorElement>) {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    event.preventDefault();
    navigate(path);
  }
  return (
    <a href={path} onClick={follow} className={className}>
      {children}
    </a>
  );
}

type CustomerListState =
  | { kind: "loading" }
  | { kind: "loaded"; customers: Customer[] }
  | { kind: "error" }
  | { kind: "unauthenticated" }
  | { kind: "forbidden" };

function CustomerList({
  navigate,
  confirmation,
  discardConfirmation,
}: {
  navigate: Navigate;
  confirmation: Customer | null;
  discardConfirmation: () => void;
}) {
  const [state, setState] = useState<CustomerListState>({ kind: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const navigation = new AbortController();
    const signal = AbortSignal.any([
      navigation.signal,
      AbortSignal.timeout(8000),
    ]);
    async function load() {
      try {
        const response = await fetch("/api/customers", {
          signal,
          cache: "no-store",
        });
        if (navigation.signal.aborted) return;
        if (response.status === 401 || response.status === 403) {
          discardConfirmation();
          setState({
            kind: response.status === 401 ? "unauthenticated" : "forbidden",
          });
          return;
        }
        if (response.status !== 200) throw new Error("List request failed");
        const value: unknown = await response.json();
        if (!Array.isArray(value) || !value.every(isCustomer))
          throw new Error("Invalid list response");
        if (!navigation.signal.aborted)
          setState({ kind: "loaded", customers: value });
      } catch {
        if (!navigation.signal.aborted) setState({ kind: "error" });
      }
    }
    void load();
    return () => navigation.abort();
  }, [attempt, discardConfirmation]);

  const denied = state.kind === "unauthenticated" || state.kind === "forbidden";
  return (
    <>
      <header className="screen-header">
        <h1 tabIndex={-1}>Customers</h1>
        {!denied && (
          <RouteLink path={createPath} navigate={navigate} className="button">
            Add customer
          </RouteLink>
        )}
      </header>
      {!denied && confirmation && (
        <p className="confirmed" role="status">
          Saved customer {confirmation.name}.
        </p>
      )}
      {state.kind === "loading" && <p role="status">Loading customers…</p>}
      {state.kind === "loaded" &&
        (state.customers.length === 0 ? (
          <p>No customers yet.</p>
        ) : (
          <table>
            <caption className="visually-hidden">
              Customers in this tenant
            </caption>
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Email</th>
              </tr>
            </thead>
            <tbody>
              {state.customers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.name}</td>
                  <td>{customer.email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ))}
      {state.kind === "error" && (
        <div>
          <p role="alert">We could not load customers.</p>
          <button
            type="button"
            onClick={() => {
              setState({ kind: "loading" });
              setAttempt(attempt + 1);
            }}
          >
            Try again
          </button>
        </div>
      )}
      {state.kind === "unauthenticated" && (
        <p role="alert">
          Your session has ended. Return to the host application.
        </p>
      )}
      {state.kind === "forbidden" && (
        <p role="alert">You do not have permission to view customers.</p>
      )}
    </>
  );
}

type SaveState =
  | { kind: "ready" | "saving" }
  | { kind: "blocked"; message: string }
  | SaveFailure;
const unresolvedSave = "customer-admin.unresolved-save";
const storageUnavailable = {
  kind: "blocked",
  message:
    "This browser could not preserve save recovery. Return to customers.",
} as const;

function initialSaveState(): SaveState {
  try {
    return sessionStorage.getItem(unresolvedSave)
      ? saveFailure(null)
      : { kind: "ready" };
  } catch {
    return storageUnavailable;
  }
}

export function CustomerForm({
  navigate,
  onCreated,
}: {
  navigate: Navigate;
  onCreated: (customer: Customer) => void;
}) {
  const [state, setState] = useState<SaveState>(initialSaveState);
  const inFlight = useRef<AbortController | null>(null);
  const feedback = useRef<HTMLParagraphElement>(null);
  useEffect(() => () => inFlight.current?.abort(), []);
  useEffect(() => {
    if ("message" in state) feedback.current?.focus();
  }, [state]);

  const editable = state.kind === "ready" || state.kind === "error";
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editable || inFlight.current) return;
    const data = new FormData(event.currentTarget);
    const navigation = new AbortController();
    inFlight.current = navigation;
    const signal = AbortSignal.any([
      navigation.signal,
      AbortSignal.timeout(8000),
    ]);
    let sent = false;
    setState({ kind: "saving" });
    try {
      const tenant = await sessionTenant(signal);
      signal.throwIfAborted();
      try {
        if (sessionStorage.getItem(unresolvedSave)) {
          setState(saveFailure(null));
          return;
        }
        // Preserve only the unresolved-write marker across history and reload.
        sessionStorage.setItem(unresolvedSave, "pending");
      } catch {
        setState(storageUnavailable);
        return;
      }
      sent = true;
      const response = await fetch("/api/customers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_id: tenant,
          name: data.get("name"),
          email: data.get("email"),
        }),
        signal,
      });
      if (navigation.signal.aborted) return;
      if (response.status !== 201) {
        const failure = saveFailure(response.status);
        if (failure.kind !== "unconfirmed")
          sessionStorage.removeItem(unresolvedSave);
        setState(failure);
        return;
      }
      const customer: unknown = await response.json();
      if (!isCustomer(customer) || customer.tenant_id !== tenant)
        throw new Error("Invalid create response");
      if (!navigation.signal.aborted) {
        sessionStorage.removeItem(unresolvedSave);
        onCreated(customer);
      }
    } catch {
      if (!navigation.signal.aborted) {
        setState(
          sent
            ? saveFailure(null)
            : {
                kind: "unauthenticated",
                message:
                  "Your session is unavailable. Return to the host application.",
              },
        );
      }
    } finally {
      inFlight.current = null;
    }
  }
  function returnToList(path: string) {
    if (state.kind === "unconfirmed") {
      try {
        sessionStorage.removeItem(unresolvedSave);
      } catch {
        setState(storageUnavailable);
        return;
      }
    }
    navigate(path);
  }
  return (
    <>
      <h1 tabIndex={-1}>Add customer</h1>
      <form onSubmit={submit}>
        {"message" in state && (
          <p ref={feedback} tabIndex={-1} role="alert">
            {state.message}
          </p>
        )}
        <fieldset disabled={!editable}>
          <label htmlFor="customer-name">Name</label>
          <input id="customer-name" name="name" autoComplete="name" required />
          <label htmlFor="customer-email">Email</label>
          <input
            id="customer-email"
            name="email"
            type="email"
            autoComplete="email"
            required
          />
        </fieldset>
        <div className="actions">
          {editable && <button type="submit">Save customer</button>}
          {editable && (
            <RouteLink path={listPath} navigate={navigate}>
              Cancel
            </RouteLink>
          )}
          {!editable && state.kind !== "saving" && (
            <RouteLink path={listPath} navigate={returnToList}>
              Back to customers
            </RouteLink>
          )}
          {state.kind === "saving" && <p role="status">Saving customer…</p>}
        </div>
      </form>
    </>
  );
}

export function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [confirmation, setConfirmation] = useState<Customer | null>(null);
  const main = useRef<HTMLElement>(null);
  // React state setters are stable. Use a stable callback when reloading list data.
  const discardConfirmation = useRef(() => setConfirmation(null)).current;
  useEffect(() => {
    const update = () => setPath(window.location.pathname);
    window.addEventListener("popstate", update);
    return () => window.removeEventListener("popstate", update);
  }, []);
  useEffect(() => {
    const heading = main.current?.querySelector("h1");
    if (heading) {
      document.title = heading.textContent || "Customers";
      heading.focus();
    }
  }, [path]);
  function navigate(destination: string) {
    window.history.pushState(null, "", destination);
    setPath(destination);
  }
  function created(customer: Customer) {
    setConfirmation(customer);
    navigate(listPath);
  }
  return (
    <main ref={main}>
      {path === createPath ? (
        <CustomerForm navigate={navigate} onCreated={created} />
      ) : path === "/" || path === listPath ? (
        <CustomerList
          navigate={navigate}
          confirmation={confirmation}
          discardConfirmation={discardConfirmation}
        />
      ) : (
        <>
          <h1 tabIndex={-1}>Page not found</h1>
          <RouteLink path={listPath} navigate={navigate}>
            Back to customers
          </RouteLink>
        </>
      )}
    </main>
  );
}
