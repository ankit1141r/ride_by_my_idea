"""
Unit tests for fare calculation service

Tests specific examples and edge cases for fare calculation logic.
Validates Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

import pytest
from app.services.fare_service import (
    calculate_estimated_fare,
    calculate_final_fare,
    get_fare_summary,
    BASE_FARE,
    PER_KM_RATE
)


class TestEstimatedFareCalculation:
    """Test estimated fare calculation"""
    
    def test_basic_fare_calculation_5km(self):
        """Test exact fare for 5km ride: ₹30 + (5 * ₹12) = ₹90"""
        fare = calculate_estimated_fare(distance_km=5.0, surge_multiplier=1.0)
        
        assert fare.base_fare == 30.0
        assert fare.distance_charge == 60.0
        assert fare.surge_multiplier == 1.0
        assert fare.total_fare == 90.0
        assert fare.breakdown.base == 30.0
        assert fare.breakdown.per_km == 12.0
        assert fare.breakdown.distance == 5.0
        assert fare.breakdown.surge == 1.0
    
    def test_zero_distance_ride(self):
        """Test fare for zero distance (base fare only)"""
        fare = calculate_estimated_fare(distance_km=0.0, surge_multiplier=1.0)
        
        assert fare.base_fare == 30.0
        assert fare.distance_charge == 0.0
        assert fare.total_fare == 30.0
    
    def test_surge_pricing_2x(self):
        """Test surge pricing with 2x multiplier"""
        fare = calculate_estimated_fare(distance_km=5.0, surge_multiplier=2.0)
        
        # Base calculation: (30 + 60) * 2 = 180
        assert fare.base_fare == 30.0
        assert fare.distance_charge == 60.0
        assert fare.surge_multiplier == 2.0
        assert fare.total_fare == 180.0
    
    def test_surge_pricing_1_5x(self):
        """Test surge pricing with 1.5x multiplier"""
        fare = calculate_estimated_fare(distance_km=10.0, surge_multiplier=1.5)
        
        # Base calculation: (30 + 120) * 1.5 = 225
        assert fare.base_fare == 30.0
        assert fare.distance_charge == 120.0
        assert fare.surge_multiplier == 1.5
        assert fare.total_fare == 225.0
    
    def test_default_surge_multiplier(self):
        """Test that default surge multiplier is 1.0"""
        fare = calculate_estimated_fare(distance_km=5.0)
        
        assert fare.surge_multiplier == 1.0
        assert fare.total_fare == 90.0
    
    def test_fractional_distance(self):
        """Test fare calculation with fractional distance"""
        fare = calculate_estimated_fare(distance_km=7.5, surge_multiplier=1.0)
        
        # Base calculation: 30 + (7.5 * 12) = 30 + 90 = 120
        assert fare.base_fare == 30.0
        assert fare.distance_charge == 90.0
        assert fare.total_fare == 120.0
    
    def test_fare_breakdown_completeness(self):
        """Test that fare breakdown includes all required fields"""
        fare = calculate_estimated_fare(distance_km=5.0, surge_multiplier=1.5)
        
        assert hasattr(fare, 'breakdown')
        assert fare.breakdown.base == BASE_FARE
        assert fare.breakdown.per_km == PER_KM_RATE
        assert fare.breakdown.distance == 5.0
        assert fare.breakdown.surge == 1.5


class TestFinalFareCalculation:
    """Test final fare calculation with fare protection"""
    
    def test_final_fare_within_20_percent(self):
        """Test final fare when actual is within 20% of estimated"""
        # Estimated: 5km = ₹90
        # Actual: 5.5km = ₹96 (6.67% difference, within 20%)
        estimated = 90.0
        fare = calculate_final_fare(
            actual_distance_km=5.5,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        # Should charge actual fare
        assert fare.total_fare == 96.0
        assert fare.breakdown.distance == 5.5
    
    def test_fare_protection_at_20_percent_threshold(self):
        """Test fare protection at exactly 20% difference"""
        # Estimated: 5km = ₹90
        # Actual: 6km = ₹102 (13.33% difference, within 20%)
        estimated = 90.0
        fare = calculate_final_fare(
            actual_distance_km=6.0,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        # Should charge actual fare (within threshold)
        assert fare.total_fare == 102.0
    
    def test_fare_protection_exceeds_20_percent(self):
        """Test fare protection when actual exceeds 20% of estimated"""
        # Estimated: 5km = ₹90
        # Actual: 8km = ₹126 (40% difference, exceeds 20%)
        estimated = 90.0
        fare = calculate_final_fare(
            actual_distance_km=8.0,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        # Should cap at estimated fare
        assert fare.total_fare == estimated
        assert fare.breakdown.distance == 8.0  # Breakdown shows actual distance
    
    def test_fare_protection_actual_lower_than_estimated(self):
        """Test fare protection when actual is lower than estimated"""
        # Estimated: 5km = ₹90
        # Actual: 3km = ₹66 (26.67% difference, exceeds 20%)
        estimated = 90.0
        fare = calculate_final_fare(
            actual_distance_km=3.0,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        # Should cap at estimated fare (rider pays estimated even if actual is lower)
        assert fare.total_fare == estimated
    
    def test_final_fare_with_surge_pricing(self):
        """Test final fare calculation with surge pricing"""
        # Estimated: 5km with 2x surge = ₹180
        # Actual: 5.5km with 2x surge = ₹192 (6.67% difference)
        estimated = 180.0
        fare = calculate_final_fare(
            actual_distance_km=5.5,
            estimated_fare=estimated,
            surge_multiplier=2.0
        )
        
        # Should charge actual fare (within 20%)
        assert fare.total_fare == 192.0
        assert fare.surge_multiplier == 2.0
    
    def test_final_fare_exact_match(self):
        """Test final fare when actual matches estimated exactly"""
        estimated = 90.0
        fare = calculate_final_fare(
            actual_distance_km=5.0,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        assert fare.total_fare == 90.0


class TestFareSummary:
    """Test fare summary generation"""
    
    def test_fare_summary_format(self):
        """Test that fare summary returns correct format"""
        fare = calculate_estimated_fare(distance_km=5.0, surge_multiplier=1.5)
        summary = get_fare_summary(fare)
        
        assert "base_fare" in summary
        assert "distance_charge" in summary
        assert "surge_multiplier" in summary
        assert "total_fare" in summary
        
        assert summary["base_fare"] == 30.0
        assert summary["distance_charge"] == 60.0
        assert summary["surge_multiplier"] == 1.5
        assert summary["total_fare"] == 135.0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_long_distance(self):
        """Test fare calculation for maximum distance within Indore"""
        # Indore city diameter is roughly 20-25km
        fare = calculate_estimated_fare(distance_km=25.0, surge_multiplier=1.0)
        
        # 30 + (25 * 12) = 30 + 300 = 330
        assert fare.total_fare == 330.0
    
    def test_rounding_precision(self):
        """Test that fares are rounded to 2 decimal places"""
        fare = calculate_estimated_fare(distance_km=3.333, surge_multiplier=1.0)
        
        # 30 + (3.333 * 12) = 30 + 39.996 = 69.996
        assert fare.total_fare == 70.0  # Should round to 2 decimals
    
    def test_high_surge_multiplier(self):
        """Test fare with high surge multiplier (3x)"""
        fare = calculate_estimated_fare(distance_km=5.0, surge_multiplier=3.0)
        
        # (30 + 60) * 3 = 270
        assert fare.total_fare == 270.0
    
    def test_fare_protection_edge_case_exactly_20_percent_higher(self):
        """Test fare protection at exactly 20% higher"""
        # Estimated: ₹100
        # Actual should be ₹120 (exactly 20% higher)
        estimated = 100.0
        # To get ₹120: (30 + distance * 12) = 120 → distance = 7.5km
        fare = calculate_final_fare(
            actual_distance_km=7.5,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        # At exactly 20%, should charge actual
        assert fare.total_fare == 120.0
    
    def test_fare_protection_edge_case_just_over_20_percent(self):
        """Test fare protection just over 20% threshold"""
        # Estimated: ₹100
        # Actual: ₹121 (21% higher, exceeds threshold)
        estimated = 100.0
        # To get ₹121: (30 + distance * 12) = 121 → distance ≈ 7.58km
        fare = calculate_final_fare(
            actual_distance_km=7.58,
            estimated_fare=estimated,
            surge_multiplier=1.0
        )
        
        # Just over 20%, should cap at estimated
        assert fare.total_fare == estimated
