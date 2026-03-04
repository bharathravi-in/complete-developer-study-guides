# 📅 Day 26 – React Native Basics

## 🎯 Learning Goals
- Understand React Native fundamentals
- Learn core components and APIs
- Navigate between screens
- Share code between web and native

---

## 📚 Theory

### React Native Fundamentals

```tsx
// Key Differences from React Web:

// 1. Components
// Web: <div>, <span>, <p>, <img>
// Native: <View>, <Text>, <Image>

import { View, Text, Image, ScrollView, TouchableOpacity } from 'react-native';

function WelcomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to React Native!</Text>
      <Image 
        source={{ uri: 'https://example.com/image.png' }}
        style={styles.image}
      />
      <TouchableOpacity style={styles.button} onPress={() => alert('Pressed!')}>
        <Text style={styles.buttonText}>Press Me</Text>
      </TouchableOpacity>
    </View>
  );
}

// 2. Styling (StyleSheet, no CSS)
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 10,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

// 3. No onClick, use onPress
// Web: onClick
// Native: onPress, onLongPress, onPressIn, onPressOut

// 4. Flexbox is default (column direction)
// Web: display: flex required, row default
// Native: Flex is default, column is default

// 5. No window, document
// Use Dimensions, Platform APIs
import { Dimensions, Platform } from 'react-native';

const { width, height } = Dimensions.get('window');
const isIOS = Platform.OS === 'ios';
```

### Core Components

```tsx
import {
  View,
  Text,
  Image,
  TextInput,
  ScrollView,
  FlatList,
  TouchableOpacity,
  Pressable,
  SafeAreaView,
  StatusBar,
  ActivityIndicator,
  Modal,
  Switch,
} from 'react-native';

// Text Input
function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <View>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
    </View>
  );
}

// FlatList (virtualized list)
interface Item {
  id: string;
  title: string;
}

function ItemList({ items }: { items: Item[] }) {
  return (
    <FlatList
      data={items}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <View style={styles.item}>
          <Text>{item.title}</Text>
        </View>
      )}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      ListEmptyComponent={<Text>No items</Text>}
      ListHeaderComponent={<Text style={styles.header}>Items</Text>}
      refreshing={isRefreshing}
      onRefresh={handleRefresh}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
    />
  );
}

// SafeAreaView (handles notches, status bar)
function Screen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" />
      <ScrollView>
        {/* Content */}
      </ScrollView>
    </SafeAreaView>
  );
}

// Pressable (modern touch handling)
function PressableButton() {
  return (
    <Pressable
      style={({ pressed }) => [
        styles.button,
        pressed && styles.buttonPressed,
      ]}
      onPress={handlePress}
    >
      {({ pressed }) => (
        <Text style={[styles.text, pressed && styles.textPressed]}>
          {pressed ? 'Pressed!' : 'Press Me'}
        </Text>
      )}
    </Pressable>
  );
}
```

### Navigation (React Navigation)

```tsx
// Install: npm install @react-navigation/native @react-navigation/native-stack

import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Details: { itemId: number; title: string };
  Profile: { userId: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ title: 'Welcome' }}
        />
        <Stack.Screen 
          name="Details" 
          component={DetailsScreen}
          options={({ route }) => ({ title: route.params.title })}
        />
        <Stack.Screen name="Profile" component={ProfileScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Screen components
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type HomeProps = NativeStackScreenProps<RootStackParamList, 'Home'>;

function HomeScreen({ navigation }: HomeProps) {
  return (
    <View>
      <Text>Home Screen</Text>
      <Button
        title="Go to Details"
        onPress={() => navigation.navigate('Details', {
          itemId: 42,
          title: 'Item Details',
        })}
      />
    </View>
  );
}

type DetailsProps = NativeStackScreenProps<RootStackParamList, 'Details'>;

function DetailsScreen({ route, navigation }: DetailsProps) {
  const { itemId, title } = route.params;
  
  return (
    <View>
      <Text>Details: {title}</Text>
      <Text>ID: {itemId}</Text>
      <Button title="Go Back" onPress={() => navigation.goBack()} />
    </View>
  );
}

// Tab Navigator
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator>
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Icon name="home" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}
```

### Cross-Platform Code Sharing

```tsx
// 1. Platform-specific files
// Button.ios.tsx
// Button.android.tsx
// Button.web.tsx (with react-native-web)

// React Native automatically picks the right file
import Button from './Button'; // Picks .ios.tsx on iOS, etc.

// 2. Platform module
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.OS === 'ios' ? 20 : 0,
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 } },
      android: { elevation: 4 },
      web: { boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
    }),
  },
});

// 3. Shared business logic
// src/shared/hooks/useAuth.ts - works everywhere
// src/shared/utils/validators.ts - works everywhere
// src/shared/types/index.ts - works everywhere

// Project structure for code sharing:
// 
// packages/
// ├── shared/           # Shared business logic
// │   ├── hooks/
// │   ├── utils/
// │   └── types/
// ├── ui/               # Shared UI components (cross-platform)
// │   ├── Button/
// │   │   ├── Button.tsx      # Shared logic
// │   │   ├── Button.web.tsx  # Web-specific render
// │   │   └── Button.native.tsx
// │   └── Input/
// ├── web/              # React web app
// └── mobile/           # React Native app

// 4. Cross-platform with Expo
// expo-router for web + mobile routing
// Solito for Next.js + React Native
```

### Expo vs Bare React Native

```tsx
// Expo (Recommended for most projects)
// ✅ Managed workflow - easy setup
// ✅ OTA updates
// ✅ Rich SDK (camera, location, etc.)
// ✅ expo-router for file-based routing
// ⚠️ Some native modules limited

// Create Expo project
// npx create-expo-app my-app

// Expo Router example
// app/_layout.tsx
import { Stack } from 'expo-router';

export default function Layout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: 'Home' }} />
      <Stack.Screen name="[id]" options={{ title: 'Details' }} />
    </Stack>
  );
}

// app/index.tsx
import { Link } from 'expo-router';

export default function Home() {
  return (
    <View>
      <Text>Home</Text>
      <Link href="/123">Go to item 123</Link>
    </View>
  );
}

// app/[id].tsx
import { useLocalSearchParams } from 'expo-router';

export default function Details() {
  const { id } = useLocalSearchParams();
  return <Text>Item: {id}</Text>;
}
```

---

## ✅ Task: Build Mobile App Shell

Create a React Native app with:
- Tab navigation (Home, Search, Profile)
- Stack navigation within tabs
- List with pull-to-refresh
- Form with validation
- Platform-specific styling

---

## 🎯 Interview Questions & Answers

### Q1: React vs React Native differences?
**Answer:** Different primitives (View vs div), StyleSheet vs CSS, no DOM (no window/document), different event handling (onPress vs onClick), Flexbox defaults (column vs row), platform-specific APIs needed.

### Q2: How do you optimize FlatList performance?
**Answer:** Use `keyExtractor`, `getItemLayout` for fixed heights, `removeClippedSubviews`, `windowSize` tuning, memoize `renderItem`, avoid inline functions, use `useMemo` for data transformations.

### Q3: Expo vs bare React Native?
**Answer:** Expo: faster development, managed updates, rich SDK, limited native module access. Bare: full native access, more complex setup. Expo "eject" no longer needed - use EAS Build for custom native code.

---

## ✅ Completion Checklist

- [ ] Understand RN fundamentals
- [ ] Know core components
- [ ] Implement navigation
- [ ] Share code cross-platform
- [ ] Built mobile app shell

---

**Previous:** [Day 25 - Animations](../day-25/README.md)  
**Next:** [Day 27 - AI + React](../day-27/README.md)
