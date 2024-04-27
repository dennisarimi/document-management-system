# app.py
import io
from flask import Flask, request, jsonify, send_file
from flask_migrate import Migrate
from flask_app.config import Config
from flask_app.models import db, Document

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    migrate.init_app(app, db)
    
    @app.route('/')
    def hello():
        return 'Hello, World!'
    
    # Upload Endpoint
    @app.route('/upload', methods=['POST'])
    def upload_document():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
    
        name = request.form['name']
        category = request.form['category']
        file_data = request.files['file'].read()
        document = Document(name=name, category=category, file_data=file_data)
        document.save_to_db()
        return jsonify({'message': 'File uploaded successfully'}), 200
    
    # View all documents
    @app.route('/documents', methods=['GET'])
    def get_documents():
        documents = Document.query.all()
        return jsonify([document.serialize() for document in documents])
    
    # View one document
    @app.route('/documents/<int:document_id>', methods=['GET'])
    def get_document(document_id):
        document = Document.query.filter_by(id=document_id).first()
        return jsonify(document.serialize())
    
    # View all previous versions
    @app.route('/documents/<int:document_id>/versions')
    def get_all_versions():
        pass
    
    # View specific previous version
    @app.route('/documents/<int:document_id>/versions/<int:version_number>')
    def get_specific_version():
        pass
    
    # Delete Endpoint
    @app.route('/documents/<int:document_id>/delete', methods=['DELETE'])
    def delete_document(document_id):
        document = Document.query.get_or_404(document_id)
        document.delete_from_db()
        return jsonify({'message': 'Document deleted successfully'}), 200
    
    # Download Endpoint
    @app.route('/documents/<int:document_id>/download')
    def download_document(document_id):
        document = Document.query.get_or_404(document_id)
        return send_file(
            io.BytesIO(document.file_data),  # Provide the file data as a BytesIO object
            download_name=document.name,  # Set the downloaded file name
            as_attachment=True,  # Force the browser to treat it as an attachment
            mimetype='application/' + document.extension
        )
    
    # Search Endpoint
    @app.route('/search')
    def search_documents():
        # Implement search functionality based on query parameters
        # Example: search by document name
        name = request.args.get('name')
        if name:
            documents = Document.query.filter(Document.name.ilike(f'%{name}%')).all()
            return jsonify([document.serialize() for document in documents])
        else:
            return jsonify({'error': 'Missing query parameter "name"'}), 400

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
