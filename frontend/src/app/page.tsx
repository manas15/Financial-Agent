'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to watchlist immediately
    router.push('/watchlist')
  }, [router])

  return null
}
