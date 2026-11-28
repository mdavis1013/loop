
import { useLocation, useParams, Link } from 'react-router-dom';

import {
    CATEGORIES,
    getPlaceCategory
} from '../Utilities/PlaceCategories';

import './PlaceDetails.css';

function PlaceDetails() {
    const { placeId } = useParams();
    const { state } = useLocation();

    const place = state?.place;

    if (!place || String(place.id) !== placeId) {
        return (
            <main className="place-details">
                <h2>Place information unavailable</h2>
                <p>Return to Explore to select a location.</p>
                <Link to="/explore">← Back to Explore</Link>
            </main>
        );
    }

    const category = CATEGORIES[getPlaceCategory(place)];

    return (
        <main className="place-details">

            <Link to="/explore" className="back-to-explore">
                ← Back to Explore
            </Link>

            <div
                className="place-hero"
                style={{
                    backgroundColor: `${category.color}20`
                }}
            >
                <span className="place-hero-icon">
                    {category.icon}
                </span>
            </div>

            <section className="place-information">

                <span
                    className="details-category"
                    style={{
                        color: category.color,
                        backgroundColor: `${category.color}20`
                    }}
                >
                    {category.label}
                </span>

                <h1>{place.name}</h1>

                <p className="details-address">
                    📍 {place.address}
                </p>

                <div className="details-rating">
                    {place.averageRating != null &&
                     place.reviewCount > 0 ? (
                        <p>
                            ⭐ {Number(place.averageRating).toFixed(1)}
                            {' '}({place.reviewCount} Loop reviews)
                        </p>
                    ) : (
                        <p>No Loop reviews yet</p>
                    )}
                </div>

                <button
                    className="add-collection-button"
                    type="button"
                    disabled
                >
                    + Add to Collection
                </button>

            </section>

            <section className="place-about">
                <h2>About this place</h2>

                <p>
                    {place.description ||
                        `${place.name} is located at ${place.address}.`}
                </p>
            </section>

            <section className="place-reviews">
                <div className="reviews-heading">
                    <h2>Community Reviews</h2>

                    <button
                        className="write-review-button"
                        type="button"
                        disabled
                    >
                        + Write a Review
                    </button>
                </div>

                <div className="empty-reviews">
                    <span>☆</span>
                    <h3>Be the first to review!</h3>
                    <p>
                        Share your experience with the Loop community.
                    </p>
                </div>
            </section>

        </main>
    );
}

export default PlaceDetails;
