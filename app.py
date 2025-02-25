from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services.agency_service import get_all_agencies, get_agency_with_children, get_total_statistics
from services.corrections_service import get_all_corrections

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.route('/api/statistics/total', methods=['GET'])
def get_statistics():
    """Get total statistics across all agencies."""
    try:
        stats = get_total_statistics()
        return jsonify({
            'total_agencies': stats['total_agencies'] or 0,
            'total_sections': stats['total_sections'] or 0,
            'total_words': stats['total_words'] or 0
        })
    except Exception as e:
        print(f"Error fetching total statistics: {e}")
        return jsonify({"error": "Failed to fetch total statistics"}), 500

@app.route('/api/agencies', methods=['GET'])
def get_agencies():
    """Get all agencies with their latest statistics."""
    try:
        agencies = get_all_agencies()
        return jsonify([{
            'id': agency['id'],
            'name': agency['name'],
            'slug': agency['slug'],
            'word_count': agency['word_count'] or 0,
            'sections': agency['section_count'] or 0,
            'snapshot_date': agency['snapshot_date'].isoformat() if agency['snapshot_date'] else None,
            'created_at': agency['created_at'].isoformat(),
            'updated_at': agency['updated_at'].isoformat()
        } for agency in agencies])
    except Exception as e:
        print(f"Error fetching agencies: {e}")
        return jsonify({"error": "Failed to fetch agencies"}), 500

@app.route('/api/agencies/<slug>', methods=['GET'])
def get_agency_details(slug):
    """Get agency details and its child agencies."""
    try:
        agency, children = get_agency_with_children(slug)
        if not agency:
            return jsonify({"error": "Agency not found"}), 404

        return jsonify({
            "agency": {
                'id': agency['id'],
                'name': agency['name'],
                'slug': agency['slug'],
                'word_count': agency['word_count'] or 0,
                'sections': agency['section_count'] or 0,
                'snapshot_date': agency['snapshot_date'].isoformat() if agency['snapshot_date'] else None,
                'created_at': agency['created_at'].isoformat(),
                'updated_at': agency['updated_at'].isoformat()
            },
            "children": [{
                'id': child['id'],
                'name': child['name'],
                'slug': child['slug'],
                'word_count': child['word_count'] or 0,
                'sections': child['section_count'] or 0,
                'snapshot_date': child['snapshot_date'].isoformat() if child['snapshot_date'] else None,
                'created_at': child['created_at'].isoformat(),
                'updated_at': child['updated_at'].isoformat()
            } for child in children]
        })
    except Exception as e:
        print(f"Error fetching agency details: {e}")
        return jsonify({"error": "Failed to fetch agency details"}), 500

@app.route('/api/corrections', methods=['GET'])
def get_corrections():
    """Get yearly corrections data."""
    try:
        corrections = get_all_corrections()
        return jsonify([
            {"year": row["year"], "corrections": row["count"]}
            for row in corrections
        ])
    except Exception as e:
        print(f"Error fetching corrections data: {e}")
        return jsonify({"error": "Failed to fetch corrections data"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 