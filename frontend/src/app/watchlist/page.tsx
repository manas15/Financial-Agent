'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Title,
  Text,
  Card,
  Group,
  Stack,
  Button,
  Table,
  Badge,
  ActionIcon,
  TextInput,
  Loader,
  Center,
  rem,
  Grid,
  Paper,
  ScrollArea,
  Textarea,
  Divider,
  Alert,
  Drawer,
  Avatar,
  Tabs,
  Menu,
  UnstyledButton,
  Tooltip,
  Anchor
} from '@mantine/core'
import {
  IconSearch,
  IconPlus,
  IconTrash,
  IconTrendingUp,
  IconTrendingDown,
  IconInfoCircle,
  IconRobot,
  IconSend,
  IconUser,
  IconMessage,
  IconClock,
  IconDots,
  IconX,
  IconBrain,
  IconSparkles
} from '@tabler/icons-react'
import { useApp } from '@/providers/AppProvider'
import { notifications } from '@mantine/notifications'
import { useDisclosure } from '@mantine/hooks'
import Link from 'next/link'
import axios from 'axios'

// Stock symbol mapping for company name search
const STOCK_MAPPINGS = {
  'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL',
  'amazon': 'AMZN', 'tesla': 'TSLA', 'meta': 'META', 'facebook': 'META',
  'netflix': 'NFLX', 'nvidia': 'NVDA', 'adobe': 'ADBE', 'salesforce': 'CRM',
  'jpmorgan': 'JPM', 'berkshire': 'BRK.A', 'visa': 'V', 'mastercard': 'MA',
  'johnson': 'JNJ', 'procter': 'PG', 'cocacola': 'KO', 'pepsi': 'PEP',
  'walmart': 'WMT', 'homedepot': 'HD', 'disney': 'DIS', 'mcdonald': 'MCD'
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  financial_data_used?: any
  error?: string
}

interface ChatSession {
  session_id: string
  ticker?: string
  title: string
  last_message: string
  timestamp: string
  message_count: number
}

export default function WatchlistWithAI() {
  const { state, actions } = useApp()
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  // AI Chat States
  const [aiDrawerOpened, { open: openAiDrawer, close: closeAiDrawer }] = useDisclosure(false)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [selectedStock, setSelectedStock] = useState<string | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [activeSession, setActiveSession] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatMessages])

  // Fetch chat sessions when AI drawer opens
  useEffect(() => {
    if (aiDrawerOpened) {
      fetchChatSessions()
    }
  }, [aiDrawerOpened])

  const fetchChatSessions = async () => {
    try {
      const response = await axios.get('http://localhost:8000/ai/watchlist/chat-sessions')
      setChatSessions(response.data.sessions || [])
    } catch (error) {
      console.error('Failed to fetch chat sessions:', error)
    }
  }

  const handleSearch = () => {
    if (!searchTerm.trim()) return

    setIsLoading(true)
    const searchLower = searchTerm.toLowerCase().trim()
    
    // Direct symbol search
    let symbol = searchTerm.toUpperCase().trim()
    
    // Company name mapping
    if (STOCK_MAPPINGS[searchLower]) {
      symbol = STOCK_MAPPINGS[searchLower]
    }
    
    actions.addToWatchlist(symbol).then(() => {
      setSearchTerm('')
      notifications.show({
        title: 'Stock Added',
        message: `${symbol} has been added to your watchlist`,
        color: 'green',
      })
    }).catch((error) => {
      notifications.show({
        title: 'Error',
        message: 'Failed to add stock to watchlist',
        color: 'red',
      })
    }).finally(() => {
      setIsLoading(false)
    })
  }

  const handleRemoveStock = (symbol: string) => {
    actions.removeFromWatchlist(symbol).then(() => {
      notifications.show({
        title: 'Stock Removed',
        message: `${symbol} has been removed from your watchlist`,
        color: 'orange',
      })
    }).catch(() => {
      notifications.show({
        title: 'Error',
        message: 'Failed to remove stock from watchlist',
        color: 'red',
      })
    })
  }

  const startChatWithStock = (ticker: string) => {
    setSelectedStock(ticker)
    setActiveSession(`watchlist_${ticker}_1`)
    setChatMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `Hi! I'm ready to analyze ${ticker} from your watchlist. What would you like to know about this stock? I can provide analysis on performance, financials, growth prospects, risks, or compare it with other stocks in your watchlist.`,
      timestamp: new Date().toISOString()
    }])
    openAiDrawer()
  }

  const startGeneralChat = () => {
    setSelectedStock(null)
    setActiveSession('watchlist_general_1')
    setChatMessages([{
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I'm your AI financial assistant. I can help you analyze your watchlist stocks, provide market insights, and make investment recommendations. What would you like to discuss?`,
      timestamp: new Date().toISOString()
    }])
    openAiDrawer()
  }

  const sendMessage = async () => {
    if (!currentMessage.trim() || chatLoading) return

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    setChatMessages(prev => [...prev, userMessage])
    setCurrentMessage('')
    setChatLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/ai/watchlist/chat', {
        query: currentMessage,
        ticker: selectedStock,
        user_id: 1  // TODO: Get from auth context
      })

      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        financial_data_used: response.data.financial_data_used,
        error: response.data.error
      }

      setChatMessages(prev => [...prev, aiMessage])
      
      // Refresh chat sessions to show new conversation
      fetchChatSessions()

      if (response.data.error) {
        notifications.show({
          title: 'AI Assistant Warning',
          message: response.data.error,
          color: 'orange',
        })
      }

    } catch (error: any) {
      console.error('Failed to send message:', error)
      
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: error.response?.data?.detail || 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        error: 'API Error'
      }

      setChatMessages(prev => [...prev, errorMessage])
      
      notifications.show({
        title: 'Connection Error',
        message: error.response?.data?.detail || 'Failed to connect to AI assistant',
        color: 'red',
      })
    } finally {
      setChatLoading(false)
    }
  }

  const loadChatSession = async (session: ChatSession) => {
    setActiveSession(session.session_id)
    setSelectedStock(session.ticker || null)
    
    // Load conversation history from the session
    try {
      const response = await axios.get(`http://localhost:8000/ai/conversation-history/${session.session_id}`)
      // Convert history to chat messages format
      // This would need to be implemented based on your history format
      setChatMessages([{
        id: 'loaded',
        role: 'assistant', 
        content: `Loaded conversation: ${session.title}`,
        timestamp: new Date().toISOString()
      }])
    } catch (error) {
      console.error('Failed to load chat session:', error)
    }
  }

  const deleteChatSession = async (sessionId: string) => {
    try {
      await axios.delete(`http://localhost:8000/ai/watchlist/chat-sessions/${sessionId}`)
      setChatSessions(prev => prev.filter(s => s.session_id !== sessionId))
      
      if (activeSession === sessionId) {
        setChatMessages([])
        setActiveSession(null)
      }
      
      notifications.show({
        title: 'Session Deleted',
        message: 'Chat session has been deleted',
        color: 'blue',
      })
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to delete chat session',
        color: 'red',
      })
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (state.watchlistLoading) {
    return (
      <Center style={{ height: '50vh' }}>
        <Loader size="lg" />
      </Center>
    )
  }

  return (
    <Container size="xl">
      <Stack gap="lg">
        {/* Header */}
        <Group justify="space-between">
          <div>
            <Title order={1}>My Watchlist</Title>
            <Text c="dimmed">Track and analyze your favorite stocks with AI assistance</Text>
          </div>
          
          <Group>
            <Button
              onClick={startGeneralChat}
              leftSection={<IconRobot size="1rem" />}
              variant="light"
            >
              AI Assistant
            </Button>
          </Group>
        </Group>

        {/* Search */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group gap="sm">
            <TextInput
              placeholder="Search stocks by symbol (AAPL) or company (Apple)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.currentTarget.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              leftSection={<IconSearch size="1rem" />}
              flex="1"
            />
            <Button
              onClick={handleSearch}
              loading={isLoading}
              leftSection={<IconPlus size="1rem" />}
            >
              Add to Watchlist
            </Button>
          </Group>
        </Card>

        {/* Watchlist Table */}
        {!state.watchlist || state.watchlist.length === 0 ? (
          <Card shadow="sm" padding="xl" radius="md" withBorder>
            <Center>
              <Stack align="center" gap="md">
                <IconInfoCircle size={48} color="gray" />
                <Text size="lg" fw={500}>Your watchlist is empty</Text>
                <Text c="dimmed" ta="center">
                  Add some stocks to your watchlist to start tracking their performance and get AI-powered insights
                </Text>
                
                <Alert color="blue" mt="md" style={{ maxWidth: '500px' }}>
                  <Group gap="sm">
                    <IconRobot size="1rem" />
                    <div>
                      <Text fw={500} size="sm">Try the AI Assistant!</Text>
                      <Text size="sm">
                        Even with an empty watchlist, you can test our AI assistant with demo stocks (AAPL, MSFT, GOOGL, AMZN, TSLA). 
                        Click the "AI Assistant" button above to start chatting!
                      </Text>
                    </div>
                  </Group>
                </Alert>
              </Stack>
            </Center>
          </Card>
        ) : (
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Instrument</Table.Th>
                  <Table.Th ta="right">Last</Table.Th>
                  <Table.Th ta="right">Change</Table.Th>
                  <Table.Th ta="right">Chg%</Table.Th>
                  <Table.Th ta="right">Volume</Table.Th>
                  <Table.Th ta="center">AI Chat</Table.Th>
                  <Table.Th ta="center">Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {state.watchlist.map((stock) => {
                  const change = stock.change || 0
                  const changePercent = stock.change_percent || 0
                  const volume = stock.volume || 0
                  const price = stock.current_price || 0

                  return (
                    <Table.Tr key={stock.id}>
                      <Table.Td>
                        <Anchor
                          component={Link}
                          href={`/stock/${stock.symbol}`}
                          fw={600}
                          size="sm"
                        >
                          {stock.symbol}
                        </Anchor>
                      </Table.Td>
                      <Table.Td ta="right" fw={600}>
                        ${price.toFixed(2)}
                      </Table.Td>
                      <Table.Td ta="right">
                        <Text c={change >= 0 ? 'green' : 'red'} fw={500}>
                          {change >= 0 ? '+' : ''}{change.toFixed(2)}
                        </Text>
                      </Table.Td>
                      <Table.Td ta="right">
                        <Badge
                          color={changePercent >= 0 ? 'green' : 'red'}
                          variant="light"
                          leftSection={
                            changePercent >= 0 ? (
                              <IconTrendingUp style={{ width: rem(12), height: rem(12) }} />
                            ) : (
                              <IconTrendingDown style={{ width: rem(12), height: rem(12) }} />
                            )
                          }
                        >
                          {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
                        </Badge>
                      </Table.Td>
                      <Table.Td ta="right">
                        <Text size="sm">
                          {volume > 1000000 ? 
                            `${(volume / 1000000).toFixed(1)}M` : 
                            volume.toLocaleString()
                          }
                        </Text>
                      </Table.Td>
                      <Table.Td ta="center">
                        <Tooltip label={`Chat about ${stock.symbol} with AI`}>
                          <ActionIcon
                            variant="light"
                            color="blue"
                            onClick={() => startChatWithStock(stock.symbol)}
                          >
                            <IconRobot size="1rem" />
                          </ActionIcon>
                        </Tooltip>
                      </Table.Td>
                      <Table.Td ta="center">
                        <ActionIcon
                          color="red"
                          variant="light"
                          onClick={() => handleRemoveStock(stock.symbol)}
                        >
                          <IconTrash size="1rem" />
                        </ActionIcon>
                      </Table.Td>
                    </Table.Tr>
                  )
                })}
              </Table.Tbody>
            </Table>
          </Card>
        )}
      </Stack>

      {/* AI Chat Drawer */}
      <Drawer
        opened={aiDrawerOpened}
        onClose={closeAiDrawer}
        title="AI Financial Assistant"
        position="right"
        size="xl"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
      >
        <Stack gap="md" style={{ height: 'calc(100vh - 120px)' }}>
          {/* Chat Sessions Sidebar */}
          <Card shadow="sm" padding="sm" radius="md" withBorder style={{ maxHeight: '200px' }}>
            <Text size="sm" fw={600} mb="xs">Recent Conversations</Text>
            <ScrollArea h={140}>
              <Stack gap="xs">
                {chatSessions.length === 0 ? (
                  <Text size="xs" c="dimmed">No previous conversations</Text>
                ) : (
                  chatSessions.map((session) => (
                    <UnstyledButton
                      key={session.session_id}
                      onClick={() => loadChatSession(session)}
                      style={{ 
                        width: '100%',
                        borderRadius: '4px',
                        backgroundColor: activeSession === session.session_id ? 'var(--mantine-color-blue-light)' : 'transparent'
                      }}
                      p="xs"
                    >
                      <Group justify="space-between" gap="xs">
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <Text size="xs" fw={500} truncate>
                            {session.title}
                          </Text>
                          <Text size="xs" c="dimmed" truncate>
                            {session.last_message}
                          </Text>
                        </div>
                        <Menu shadow="md" width={120}>
                          <Menu.Target>
                            <ActionIcon size="sm" variant="subtle">
                              <IconDots size="0.8rem" />
                            </ActionIcon>
                          </Menu.Target>
                          <Menu.Dropdown>
                            <Menu.Item
                              color="red"
                              leftSection={<IconTrash size="0.8rem" />}
                              onClick={() => deleteChatSession(session.session_id)}
                            >
                              Delete
                            </Menu.Item>
                          </Menu.Dropdown>
                        </Menu>
                      </Group>
                    </UnstyledButton>
                  ))
                )}
              </Stack>
            </ScrollArea>
          </Card>

          {/* Chat Messages */}
          <Card shadow="sm" padding="lg" radius="md" withBorder style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {selectedStock && (
              <Group mb="md">
                <Badge size="lg" color="blue">{selectedStock}</Badge>
                <Text size="sm" c="dimmed">Focused Chat</Text>
              </Group>
            )}
            
            <ScrollArea flex="1" mb="md">
              <Stack gap="md">
                {chatMessages.map((message) => (
                  <Group key={message.id} align="flex-start" gap="sm">
                    <Avatar
                      color={message.role === 'user' ? 'blue' : 'green'}
                      radius="xl"
                      size="sm"
                    >
                      {message.role === 'user' ? 
                        <IconUser size="1rem" /> :
                        <IconRobot size="1rem" />
                      }
                    </Avatar>
                    
                    <div style={{ flex: 1 }}>
                      <Paper
                        p="md"
                        bg={message.role === 'user' ? 'blue.0' : 'gray.0'}
                        radius="md"
                      >
                        <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                          {message.content}
                        </Text>
                        
                        {message.error && (
                          <Alert color="red" mt="xs" size="xs">
                            {message.error}
                          </Alert>
                        )}
                        
                        {message.financial_data_used && Object.keys(message.financial_data_used).length > 0 && (
                          <Group mt="xs">
                            <Badge size="xs" color="blue">
                              📊 Used Real Market Data
                            </Badge>
                          </Group>
                        )}
                      </Paper>
                      
                      <Text size="xs" c="dimmed" mt="xs">
                        {formatTimestamp(message.timestamp)}
                      </Text>
                    </div>
                  </Group>
                ))}
                
                {chatLoading && (
                  <Group align="flex-start" gap="sm">
                    <Avatar color="green" radius="xl" size="sm">
                      <IconRobot size="1rem" />
                    </Avatar>
                    <Paper p="md" bg="gray.0" radius="md">
                      <Group gap="xs">
                        <Loader size="xs" />
                        <Text size="sm" c="dimmed">AI is analyzing...</Text>
                      </Group>
                    </Paper>
                  </Group>
                )}
                
                <div ref={messagesEndRef} />
              </Stack>
            </ScrollArea>
            
            {/* Input Area */}
            <Divider mb="md" />
            <Group gap="sm">
              <Textarea
                flex="1"
                placeholder="Ask about your watchlist stocks..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.currentTarget.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                autosize
                minRows={1}
                maxRows={3}
                disabled={chatLoading}
              />
              <Button
                onClick={sendMessage}
                loading={chatLoading}
                leftSection={<IconSend size="1rem" />}
                disabled={!currentMessage.trim()}
              >
                Send
              </Button>
            </Group>
          </Card>
        </Stack>
      </Drawer>
    </Container>
  )
}