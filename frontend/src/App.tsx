import { useState, type FormEvent } from "react"
import { Loader2, Search, TrendingUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const API_URL = "https://dvnzil--dtsc3601-financial-similarity-fastapi-app.modal.run"

// Same 8 raw fields, same order, as the pipeline's RAW_COLUMNS.
const FIELDS = [
  { name: "Total current assets", help: "Cash + receivables + inventory, etc." },
  { name: "Total assets", help: "Sum of all assets on the balance sheet" },
  { name: "Total current liabilities", help: "Obligations due within a year" },
  { name: "Total liabilities", help: "All obligations, current and long-term" },
  { name: "Total debt", help: "Interest-bearing debt outstanding" },
  { name: "Total shareholders equity", help: "Assets minus liabilities" },
  { name: "Revenue", help: "Total revenue for the period" },
  { name: "Net Income", help: "Bottom-line profit for the period" },
] as const

type FieldName = (typeof FIELDS)[number]["name"]
type FormState = Record<FieldName, string>

const emptyForm = FIELDS.reduce((acc, field) => {
  acc[field.name] = ""
  return acc
}, {} as FormState)

interface SimilarCompany {
  ticker: string
  distance: number
}

interface SimilarResponse {
  results: SimilarCompany[]
}

function App() {
  const [form, setForm] = useState<FormState>(emptyForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<SimilarCompany[] | null>(null)

  const handleChange = (name: FieldName, value: string) => {
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setResults(null)
    setLoading(true)

    const payload = Object.fromEntries(
      FIELDS.map((field) => [field.name, parseFloat(form[field.name])])
    )

    try {
      const res = await fetch(`${API_URL}/similar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      const body = await res.json()

      if (!res.ok) {
        const detail = Array.isArray(body.detail)
          ? body.detail.map((d: { msg: string }) => d.msg).join("; ")
          : String(body.detail ?? `Request failed with status ${res.status}`)
        setError(detail)
        return
      }

      setResults((body as SimilarResponse).results)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-svh bg-background">
      <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 py-12 sm:py-16">
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="mb-1 flex size-11 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <TrendingUp className="size-5" />
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">
            Financial Ratio Similarity
          </h1>
          <p className="max-w-md text-sm text-muted-foreground">
            Enter a company&apos;s raw balance-sheet and income-statement
            figures to find the companies most similar to it by financial
            ratios.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Company financials</CardTitle>
            <CardDescription>
              All fields are required and must be positive numbers.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
              <div className="grid gap-4 sm:grid-cols-2">
                {FIELDS.map((field) => (
                  <div key={field.name} className="flex flex-col gap-1.5">
                    <Label htmlFor={field.name}>{field.name}</Label>
                    <Input
                      id={field.name}
                      type="number"
                      step="any"
                      min="0"
                      required
                      placeholder="0"
                      value={form[field.name]}
                      onChange={(e) => handleChange(field.name, e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">{field.help}</p>
                  </div>
                ))}
              </div>

              <Button type="submit" disabled={loading} className="self-start">
                {loading ? (
                  <>
                    <Loader2 className="animate-spin" />
                    Searching&hellip;
                  </>
                ) : (
                  <>
                    <Search />
                    Find similar companies
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Couldn&apos;t fetch results</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {results && (
          <Card>
            <CardHeader>
              <CardTitle>Nearest companies</CardTitle>
              <CardDescription>
                Ranked by distance in scaled financial-ratio space (lower is
                more similar).
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ticker</TableHead>
                    <TableHead className="text-right">Distance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {results.map((r) => (
                    <TableRow key={r.ticker}>
                      <TableCell className="font-medium">{r.ticker}</TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        {r.distance.toFixed(6)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default App
