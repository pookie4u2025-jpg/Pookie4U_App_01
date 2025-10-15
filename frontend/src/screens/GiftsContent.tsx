import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
  Alert,
  RefreshControl,
  Image,
} from 'react-native';
import Animated from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';
import { useTheme } from '../contexts/ThemeContext';
import { useCardAnimation, useFadeInAnimation } from '../utils/animations';
import { buttonPress } from '../utils/HapticsManager';

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

interface Gift {
  id: string;
  name: string;
  category: string;
  price_range: string;
  link: string;
  description?: string;
  image?: string;
}

export default function GiftsContent() {
  const { token } = useAuthStore();
  const { theme } = useTheme();
  
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Romantic', 'Jewelry', 'Experiences', 'Beauty', 'Food', 'Home'];

  useEffect(() => {
    fetchGifts();
  }, []);

  const fetchGifts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL}/api/gifts`);
      const data = await response.json();
      setGifts(data.gifts || []);
    } catch (error) {
      console.error('Failed to fetch gifts:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    await fetchGifts();
  };

  const openLink = async (url: string, giftName: string) => {
    if (url && url !== 'https://example.com') {
      try {
        await Linking.openURL(url);
      } catch (error) {
        Alert.alert('Error', 'Unable to open link');
      }
    } else {
      Alert.alert('Coming Soon', `${giftName} - We're working on adding shopping links!`);
    }
  };

  const filteredGifts = selectedCategory === 'All' 
    ? gifts 
    : gifts.filter(gift => gift.category === selectedCategory);

  const getPriceColor = (priceRange: string) => {
    if (priceRange.includes('Free')) return theme.success;
    if (priceRange.includes('Under ₹500')) return '#2196F3';
    if (priceRange.includes('Under ₹1000')) return theme.warning;
    if (priceRange.includes('₹1000-5000')) return '#FF5722';
    return '#9C27B0';
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Romantic': return 'heart';
      case 'Jewelry': return 'diamond';
      case 'Experiences': return 'camera';
      case 'Beauty': return 'flower';
      case 'Food': return 'restaurant';
      case 'Home': return 'home';
      default: return 'gift';
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={[styles.header, { backgroundColor: theme.surface }]}>
          <Text style={[styles.headerTitle, { color: theme.text }]}>Gift Ideas 🎁</Text>
          <Text style={[styles.headerSubtitle, { color: theme.textSecondary }]}>
            Find the perfect gift for your partner based on their preferences
          </Text>
        </View>

        {/* Category Filter */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.categoriesContainer}
          contentContainerStyle={styles.categoriesContent}
        >
          {categories.map((category, index) => (
              <AnimatedTouchable
                key={category}
                style={[
                  styles.categoryButton,
                  { backgroundColor: theme.surface, borderColor: theme.border },
                  selectedCategory === category && { backgroundColor: theme.primary, borderColor: theme.primary }
                ]}
                onPress={() => {
                  buttonPress();
                  setSelectedCategory(category);
                }}
                activeOpacity={0.7}
              >
                <Text style={[
                  styles.categoryText,
                  { color: theme.textSecondary },
                  selectedCategory === category && { color: '#fff' }
                ]}>
                  {category}
                </Text>
              </AnimatedTouchable>
          ))}
        </ScrollView>

        {/* Gifts Grid */}
        <View style={styles.giftsContainer}>
          {filteredGifts.map((gift, index) => (
            <AnimatedTouchable 
              key={gift.id} 
              style={[styles.giftCard, { backgroundColor: theme.surface }]}
              onPress={() => {
                buttonPress();
                openLink(gift.link, gift.name);
              }}
              activeOpacity={0.7}
            >
              {/* Product Image */}
              {gift.image ? (
                <Image 
                  source={{ uri: gift.image }}
                  style={styles.productImage}
                  resizeMode="cover"
                />
              ) : (
                <View style={[styles.placeholderImage, { backgroundColor: theme.primary + '20' }]}>
                  <Ionicons 
                    name={getCategoryIcon(gift.category)} 
                    size={40} 
                    color={theme.primary} 
                  />
                </View>
              )}
              
              {/* Price Tag on Image */}
              <View style={[
                styles.priceTagOverlay,
                { backgroundColor: getPriceColor(gift.price_range) }
              ]}>
                <Text style={styles.priceText}>{gift.price_range}</Text>
              </View>
              
              {/* Product Info */}
              <View style={styles.productInfo}>
                <Text style={[styles.giftName, { color: theme.text }]} numberOfLines={2}>
                  {gift.name}
                </Text>
                {gift.description && (
                  <Text style={[styles.giftDescription, { color: theme.textSecondary }]} numberOfLines={2}>
                    {gift.description}
                  </Text>
                )}
                
                <View style={[styles.shopButton, { backgroundColor: theme.primary }]}>
                  <Ionicons name="cart" size={16} color="#fff" />
                  <Text style={styles.shopButtonText}>View on Amazon</Text>
                </View>
              </View>
            </AnimatedTouchable>
          );
          })}
        </View>

        {/* Gift Tips */}
        <View style={styles.tipsSection}>
          <Text style={[styles.tipsTitle, { color: theme.text }]}>Gift Giving Tips 💝</Text>
          <View style={[styles.tipsCard, { backgroundColor: theme.surface }]}>
            <View style={styles.tip}>
              <Ionicons name="bulb" size={16} color={theme.primary} />
              <Text style={[styles.tipText, { color: theme.textSecondary }]}>
                Consider your partner's current interests and hobbies
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="heart" size={16} color={theme.primary} />
              <Text style={[styles.tipText, { color: theme.textSecondary }]}>
                Personalized gifts show more thought than expensive ones
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="time" size={16} color={theme.primary} />
              <Text style={[styles.tipText, { color: theme.textSecondary }]}>
                Experience gifts create lasting memories together
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="star" size={16} color={theme.primary} />
              <Text style={[styles.tipText, { color: theme.textSecondary }]}>
                Surprise gifts work best when they're unexpected
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    marginBottom: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
  },
  categoriesContainer: {
    marginBottom: 20,
  },
  categoriesContent: {
    paddingHorizontal: 20,
    gap: 10,
  },
  categoryButton: {
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderWidth: 1,
  },
  categoryText: {
    fontSize: 14,
    fontWeight: '600',
  },
  giftsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
    gap: 15,
  },
  giftCard: {
    width: '47%',
    borderRadius: 15,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 10,
  },
  productImage: {
    width: '100%',
    height: 150,
    backgroundColor: '#f0f0f0',
  },
  placeholderImage: {
    width: '100%',
    height: 150,
    alignItems: 'center',
    justifyContent: 'center',
  },
  priceTagOverlay: {
    position: 'absolute',
    top: 10,
    right: 10,
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  priceText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  productInfo: {
    padding: 12,
  },
  giftName: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 4,
    lineHeight: 18,
  },
  giftDescription: {
    fontSize: 11,
    marginBottom: 10,
    lineHeight: 14,
  },
  giftCategory: {
    fontSize: 12,
    marginBottom: 15,
  },
  shopButton: {
    borderRadius: 20,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 5,
    marginTop: 5,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  giftHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  categoryIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tipsSection: {
    margin: 20,
  },
  tipsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  tipsCard: {
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    marginLeft: 10,
    lineHeight: 20,
  },
});