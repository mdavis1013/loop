export const CATEGORIES = {
    restaurant: {
        label: 'Restaurants',
        color: '#D45151',
        icon: '🍴'
    },
    nature: {
        label: 'Parks & Nature',
        color: '#39945A',
        icon: '🌳'
    },
    nightlife: {
        label: 'Nightlife',
        color: '#8B5CC7',
        icon: '🪩'
    },
    coffee: {
        label: 'Coffee & Cafés',
        color: '#A97749',
        icon: '☕'
    },
    attraction: {
        label: 'Attractions',
        color: '#397FB8',
        icon: '⭐'
    },
    shopping: {
        label: 'Shopping',
        color: '#DB943B',
        icon: '🛍'
    },
    entertainment: {
        label: 'Entertainment',
        color: '#D16B9E',
        icon: '🎭'
    },
    other: {
        label: 'Other',
        color: '#7D8790',
        icon: '•'
    }
};

export function getPlaceCategory(place) {
    const primary = place.primaryType || '';
    const types = [primary, ...(place.types || [])];

    const matches = (...values) =>
        values.some(value => types.includes(value));

    if (matches('night_club', 'bar', 'pub', 'wine_bar')) {
        return 'nightlife';
    }

    if (matches('coffee_shop', 'cafe', 'tea_house', 'bakery')) {
        return 'coffee';
    }

    if (types.some(type => type.includes('restaurant'))) {
        return 'restaurant';
    }

    if (matches('park', 'national_park', 'garden', 'hiking_area', 'beach')) {
        return 'nature';
    }

    if (matches('movie_theater', 'bowling_alley', 'amusement_park', 'concert_hall')) {
        return 'entertainment';
    }

    if (matches('museum', 'tourist_attraction', 'art_gallery', 'historical_landmark', 'zoo', 'aquarium')) {
        return 'attraction';
    }

    if (primary.endsWith('_store') || matches('shopping_mall', 'store', 'market')) {
        return 'shopping';
    }

    return 'other';
}
