'use client'

import { useEffect } from 'react'
import { redirect } from 'next/navigation'
import {
  AppShell,
  Burger,
  Group,
  Text,
  NavLink,
  ThemeIcon,
  ActionIcon,
  Menu,
  Avatar,
  Divider,
  ScrollArea,
  rem,
  Badge,
  Tooltip,
  Button,
  Center,
  Loader
} from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import {
  IconDashboard,
  IconWallet,
  IconEye,
  IconChartBar,
  IconRobot,
  IconSettings,
  IconLogout,
  IconUser,
  IconSun,
  IconTrendingUp,
  IconBell,
  IconRefresh
} from '@tabler/icons-react'
import { useApp } from '@/providers/AppProvider'
import { notifications } from '@mantine/notifications'
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'

const navigationData = [
  {
    label: 'Watchlist',
    icon: IconEye,
    href: '/watchlist',
    description: 'Track stocks with AI assistance'
  }
]

export default function WatchlistLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [opened, { toggle }] = useDisclosure()
  const { state, actions } = useApp()
  const pathname = usePathname()
  const router = useRouter()

  // No longer redirect if not authenticated - allow guest browsing

  // Fetch user data if authenticated, otherwise continue as guest
  useEffect(() => {
    if (state.isAuthenticated && state.user) {
      actions.fetchWatchlist()
      actions.fetchAnalyses()
    }
  }, [state.isAuthenticated, state.user])

  const handleLogout = () => {
    actions.logout()
    router.push('/auth/login')
  }

  const refreshData = async () => {
    try {
      await Promise.all([
        actions.fetchWatchlist(),
        actions.fetchAnalyses()
      ])
      notifications.show({
        title: 'Data Refreshed',
        message: 'Watchlist and reports updated successfully',
        color: 'green',
      })
    } catch (error) {
      notifications.show({
        title: 'Refresh Failed',
        message: 'Failed to refresh data',
        color: 'red',
      })
    }
  }

  // Show loading only during app initialization
  if (state.isLoading) {
    return (
      <Center style={{ height: '100vh' }}>
        <Loader size="lg" />
      </Center>
    )
  }

  return (
    <AppShell
      header={{ height: 70 }}
      navbar={{
        width: 280,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      {/* Header */}
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            
            <Group gap="sm">
              <ThemeIcon size="lg" radius="md" variant="gradient" gradient={{ from: 'blue', to: 'cyan' }}>
                <IconTrendingUp style={{ width: rem(20), height: rem(20) }} />
              </ThemeIcon>
              <div>
                <Text fw={700} size="lg">Stock Research</Text>
                <Text size="xs" c="dimmed">AI-Powered Stock Analysis</Text>
              </div>
            </Group>
          </Group>

          <Group>
            {/* Refresh Button */}
            <Tooltip label="Refresh data">
              <ActionIcon 
                variant="light" 
                size="lg"
                onClick={refreshData}
                loading={state.watchlistLoading || state.analysisLoading}
              >
                <IconRefresh style={{ width: rem(18), height: rem(18) }} />
              </ActionIcon>
            </Tooltip>

            {/* Notifications */}
            <Tooltip label="Notifications">
              <ActionIcon variant="light" size="lg">
                <IconBell style={{ width: rem(18), height: rem(18) }} />
              </ActionIcon>
            </Tooltip>

            {/* Theme Toggle */}
            <Tooltip label="Toggle theme">
              <ActionIcon variant="light" size="lg">
                <IconSun style={{ width: rem(18), height: rem(18) }} />
              </ActionIcon>
            </Tooltip>

            {/* User Menu or Login */}
            {state.isAuthenticated ? (
              <Menu shadow="md" width={200}>
                <Menu.Target>
                  <ActionIcon variant="light" size="lg">
                    <Avatar size="sm" radius="xl">
                      {state.user?.full_name?.charAt(0) || state.user?.email?.charAt(0) || 'U'}
                    </Avatar>
                  </ActionIcon>
                </Menu.Target>

                <Menu.Dropdown>
                  <Menu.Label>
                    {state.user?.full_name || 'User'}
                    <Text size="xs" c="dimmed">{state.user?.email}</Text>
                  </Menu.Label>
                  
                  <Menu.Item leftSection={<IconUser style={{ width: rem(14), height: rem(14) }} />}>
                    Profile
                  </Menu.Item>
                  
                  <Menu.Item leftSection={<IconSettings style={{ width: rem(14), height: rem(14) }} />}>
                    Settings
                  </Menu.Item>
                  
                  <Menu.Divider />
                  
                  <Menu.Item 
                    color="red"
                    leftSection={<IconLogout style={{ width: rem(14), height: rem(14) }} />}
                    onClick={handleLogout}
                  >
                    Logout
                  </Menu.Item>
                </Menu.Dropdown>
              </Menu>
            ) : (
              <Button
                component={Link}
                href="/auth/login"
                variant="light"
                size="sm"
              >
                Login
              </Button>
            )}
          </Group>
        </Group>
      </AppShell.Header>

      {/* Navbar */}
      <AppShell.Navbar p="md">
        <AppShell.Section>
          <Text size="xs" tt="uppercase" fw={700} c="dimmed" mb="md">
            Navigation
          </Text>
        </AppShell.Section>

        <AppShell.Section grow component={ScrollArea}>
          {navigationData.map((item) => {
            const isActive = pathname === item.href
            
            return (
              <NavLink
                key={item.label}
                component={Link}
                href={item.href}
                label={item.label}
                description={item.description}
                leftSection={
                  <ThemeIcon 
                    variant={isActive ? 'filled' : 'light'} 
                    size="sm"
                    color={isActive ? 'blue' : 'gray'}
                  >
                    <item.icon style={{ width: rem(16), height: rem(16) }} />
                  </ThemeIcon>
                }
                active={isActive}
                onClick={() => opened && toggle()}
                style={{
                  borderRadius: 'var(--mantine-radius-md)',
                  marginBottom: 'var(--mantine-spacing-xs)',
                }}
              />
            )
          })}
        </AppShell.Section>

        <AppShell.Section>
          <Divider mb="md" />
          
          {/* User-specific Summary or Guest Message */}
          {state.isAuthenticated ? (
            state.watchlist && state.watchlist.length > 0 && (
              <div>
                <Text size="xs" tt="uppercase" fw={700} c="dimmed" mb="xs">
                  Your Watchlist
                </Text>
                
                <Group justify="space-between" mb="xs">
                  <Text size="sm">Tracked Stocks</Text>
                  <Text size="sm" fw={600}>
                    {state.watchlist.length}
                  </Text>
                </Group>
                
                <Group justify="space-between">
                  <Text size="sm">Reports Generated</Text>
                  <Badge 
                    color="blue"
                    variant="light"
                    size="sm"
                  >
                    {state.analyses?.length || 0}
                  </Badge>
                </Group>
              </div>
            )
          ) : (
            <div>
              <Text size="xs" tt="uppercase" fw={700} c="dimmed" mb="xs">
                Guest Mode
              </Text>
              <Text size="xs" c="dimmed">
                Login to save stocks to your personal watchlist and generate reports
              </Text>
            </div>
          )}
        </AppShell.Section>
      </AppShell.Navbar>

      {/* Main Content */}
      <AppShell.Main>
        {children}
      </AppShell.Main>
    </AppShell>
  )
}