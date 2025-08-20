"""
Data Quality Assessor Module
Analyzes dataset quality including completeness, consistency, outliers, and uniqueness
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any
from sklearn.ensemble import IsolationForest
from scipy import stats

class DataQualityAssessor:
    """
    Data Quality Assessor that analyzes dataset quality
    Checks completeness, consistency, outliers, and generates quality scores
    """
    
    def __init__(self):
        """Initialize the assessor with default thresholds"""
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.quality_thresholds = {
            'completeness': 0.95,
            'consistency': 0.90,
            'uniqueness': 0.98,
            'validity': 0.95
        }
        
    def assess_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data completeness (missing values)"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness_score = (total_cells - missing_cells) / total_cells
        
        # Per-column analysis
        column_completeness = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            col_completeness = (len(df) - missing_count) / len(df)
            column_completeness[col] = {
                'completeness_score': col_completeness,
                'missing_count': int(missing_count),
                'missing_percentage': missing_count / len(df) * 100
            }
        
        return {
            'overall_completeness': completeness_score,
            'missing_cells': int(missing_cells),
            'total_cells': int(total_cells),
            'column_analysis': column_completeness,
            'quality_grade': self._grade_score(completeness_score, self.quality_thresholds['completeness'])
        }
    
    def assess_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data consistency (data types, formats)"""
        consistency_issues = []
        column_consistency = {}
        
        for col in df.columns:
            # Check for mixed data types
            non_null_values = df[col].dropna()
            if len(non_null_values) == 0:
                continue
                
            # Detect data type consistency
            types_found = set(type(val).__name__ for val in non_null_values.head(100))
            
            # Check for string format consistency (for string columns)
            if df[col].dtype == 'object':
                # Check email format consistency
                if any('@' in str(val) for val in non_null_values.head(10)):
                    email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
                    valid_emails = sum(1 for val in non_null_values if email_pattern.match(str(val)))
                    email_consistency = valid_emails / len(non_null_values)
                    column_consistency[col] = {
                        'type': 'email',
                        'consistency_score': email_consistency,
                        'issues': f"Invalid email formats detected" if email_consistency < 0.9 else "Good"
                    }
                    continue
            
            # General consistency check
            consistency_score = 1.0 if len(types_found) == 1 else 0.7
            column_consistency[col] = {
                'type': 'mixed' if len(types_found) > 1 else list(types_found)[0],
                'consistency_score': consistency_score,
                'types_found': list(types_found),
                'issues': f"Mixed types: {types_found}" if len(types_found) > 1 else "Consistent"
            }
        
        # Calculate overall consistency
        overall_consistency = np.mean([col['consistency_score'] for col in column_consistency.values()])
        
        return {
            'overall_consistency': overall_consistency,
            'column_analysis': column_consistency,
            'quality_grade': self._grade_score(overall_consistency, self.quality_thresholds['consistency'])
        }
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numerical columns"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        outlier_analysis = {}
        
        for col in numerical_cols:
            col_data = df[col].dropna()
            if len(col_data) < 5:  # Skip if too few values
                continue
                
            # Statistical outlier detection (IQR method)
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_iqr = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            outlier_percentage = len(outliers_iqr) / len(col_data) * 100
            
            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            outliers_zscore = col_data[z_scores > 3]
            
            outlier_analysis[col] = {
                'iqr_outliers': len(outliers_iqr),
                'zscore_outliers': len(outliers_zscore),
                'outlier_percentage': outlier_percentage,
                'bounds': {'lower': lower_bound, 'upper': upper_bound},
                'severity': 'High' if outlier_percentage > 10 else 'Medium' if outlier_percentage > 5 else 'Low'
            }
        
        # Overall outlier score (lower is better)
        avg_outlier_percentage = np.mean([col['outlier_percentage'] for col in outlier_analysis.values()]) if outlier_analysis else 0
        outlier_quality_score = max(0, 1 - (avg_outlier_percentage / 100))
        
        return {
            'overall_outlier_score': outlier_quality_score,
            'average_outlier_percentage': avg_outlier_percentage,
            'column_analysis': outlier_analysis,
            'quality_grade': self._grade_score(outlier_quality_score, 0.8)
        }
    
    def assess_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data uniqueness (duplicates)"""
        total_rows = len(df)
        duplicate_rows = df.duplicated().sum()
        uniqueness_score = (total_rows - duplicate_rows) / total_rows
        
        # Per-column uniqueness
        column_uniqueness = {}
        for col in df.columns:
            unique_values = df[col].nunique()
            total_values = len(df[col].dropna())
            col_uniqueness = unique_values / total_values if total_values > 0 else 0
            
            column_uniqueness[col] = {
                'unique_values': unique_values,
                'total_values': total_values,
                'uniqueness_ratio': col_uniqueness,
                'duplicates': total_values - unique_values
            }
        
        return {
            'overall_uniqueness': uniqueness_score,
            'duplicate_rows': int(duplicate_rows),
            'total_rows': int(total_rows),
            'column_analysis': column_uniqueness,
            'quality_grade': self._grade_score(uniqueness_score, self.quality_thresholds['uniqueness'])
        }
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        
        # Run all assessments
        completeness = self.assess_completeness(df)
        consistency = self.assess_consistency(df)
        outliers = self.detect_outliers(df)
        uniqueness = self.assess_uniqueness(df)
        
        # Calculate overall quality score (weighted average)
        weights = {'completeness': 0.3, 'consistency': 0.25, 'outliers': 0.2, 'uniqueness': 0.25}
        
        overall_score = (
            completeness['overall_completeness'] * weights['completeness'] +
            consistency['overall_consistency'] * weights['consistency'] +
            outliers['overall_outlier_score'] * weights['outliers'] +
            uniqueness['overall_uniqueness'] * weights['uniqueness']
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(completeness, consistency, outliers, uniqueness)
        
        return {
            'dataset_info': {
                'rows': df.shape[0],
                'columns': df.shape[1],
                'data_types': df.dtypes.value_counts().to_dict()
            },
            'overall_quality_score': overall_score,
            'overall_grade': self._grade_score(overall_score, 0.8),
            'assessments': {
                'completeness': completeness,
                'consistency': consistency,
                'outliers': outliers,
                'uniqueness': uniqueness
            },
            'recommendations': recommendations,
            'summary': self._create_quality_summary(overall_score, completeness, consistency, outliers, uniqueness)
        }
    
    def _grade_score(self, score: float, threshold: float) -> str:
        """Convert score to letter grade"""
        if score >= threshold:
            return 'A' if score >= 0.95 else 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.5:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, completeness, consistency, outliers, uniqueness) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if completeness['overall_completeness'] < 0.9:
            recommendations.append("🔧 Handle missing values: Consider imputation or removal of incomplete records")
            
        if consistency['overall_consistency'] < 0.8:
            recommendations.append("🔧 Fix data inconsistencies: Standardize formats and data types")
            
        if outliers['average_outlier_percentage'] > 10:
            recommendations.append("🔧 Review outliers: Investigate and handle extreme values")
            
        if uniqueness['overall_uniqueness'] < 0.95:
            recommendations.append("🔧 Remove duplicates: Clean duplicate records from the dataset")
            
        if not recommendations:
            recommendations.append("✅ Data quality is good! No major issues detected")
            
        return recommendations
    
    def _create_quality_summary(self, overall_score, completeness, consistency, outliers, uniqueness) -> str:
        """Create human-readable summary"""
        grade = self._grade_score(overall_score, 0.8)
        
        issues = []
        if completeness['overall_completeness'] < 0.9:
            issues.append("missing data")
        if consistency['overall_consistency'] < 0.8:
            issues.append("inconsistency")
        if outliers['average_outlier_percentage'] > 10:
            issues.append("outliers")
        if uniqueness['overall_uniqueness'] < 0.95:
            issues.append("duplicates")
            
        if not issues:
            return f"Dataset quality is excellent (Grade {grade}). Ready for analysis."
        else:
            return f"Dataset quality is {grade}. Main issues: {', '.join(issues)}."
