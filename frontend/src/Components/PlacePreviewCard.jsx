import { useNavigate } from 'react-router-dom';
import {
    CATEGORIES,
    getPlaceCategory
} from '../Utilities/PlaceCategories';

import './PlacePreviewCard.css';

function PlacePreviewCard({ place }) {
    const navigate = useNavigate();
    const category = CATEGORIES[getPlaceCategory(place)];

    function handleViewPlace() {
        navigate(`/place/${encodeURIComponent(place.id)}`, {
            state: { place }
        });
    }

    return (
        <div className="place-preview-card">
            <span
                className="preview-category"
                style={{
                    color: category.color,
                    backgroundColor: `${category.color}20`
                }}
            >
                {category.icon} {category.label}
            </span>

            <h3 className="preview-name">
                {place.name}
            </h3>

            <div className="preview-rating">
                {place.averageRating != null && place.reviewCount > 0 ? (
                    <>
                        <span className="preview-star">★</span>
                        <strong>
                            {Number(place.averageRating).toFixed(1)}
                        </strong>
                        <span>({place.reviewCount} reviews)</span>
                    </>
                ) : (
                    <span>No Loop reviews yet</span>
                )}
            </div>

            <p className="preview-address">
                {place.address}
            </p>

            <button
                type="button"
                className="view-place-button"
                onClick={handleViewPlace}
            >
                View Place →
            </button>
        </div>
    );
}

export default PlacePreviewCard;
