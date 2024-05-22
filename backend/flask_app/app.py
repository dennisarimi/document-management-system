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
    
        name = request.form['name'].upper() # save document names in uppeercase
        category = request.form['category']
        file_data = request.files['file'].read()
        
        version_nums = Document.query.filter_by(name=name).all()
        
        document = Document(name=name, version=(len(version_nums) + 1), category=category, file_data=file_data)
        document.save_to_db()
        return jsonify({'message': 'File uploaded successfully'}), 200
    
    # View all documents
    @app.route('/documents', methods=['GET'])
    def get_documents():
        documents = Document.query.all()
        return jsonify([document.serialize() for document in documents])
    
    # Delete Endpoint
    @app.route('/documents/delete', methods=['DELETE'])
    def delete_document(document_id):
        id = request.args.get('id')
        
        document = Document.query.get_or_404(id)
        document.delete_from_db()
        return jsonify({'message': 'Document deleted successfully'}), 200
    
    # Delete All
    @app.route('/documents/delete/all', methods=['DELETE'])
    def delete_all_documents():
        db.session.query(Document).delete()
        db.session.commit()
        return jsonify({'message': 'All documents deleted successfully'}), 200
    
    # Download Endpoint
    @app.route('/documents/download')
    def download_document():
        id = request.args.get('id')
        
        document = Document.query.get_or_404(id)
        return send_file(
            io.BytesIO(document.file_data),  # Provide the file data as a BytesIO object
            download_name=document.name,  # Set the downloaded file name
            as_attachment=True,  # Force the browser to treat it as an attachment
        )
    
    # Search Endpoint
    @app.route('/search')
    def search_documents():
        # Search by id, name, or name and version number
        id = request.args.get('id')
        name = request.args.get('name')
        version = request.args.get('version')
        
        if id:
            document = Document.query.filter_by(id=id).first()
            return jsonify(document.serialize())
        
        if name and not version:
            documents = Document.query.filter_by(name=name).all()
            return jsonify([document.serialize() for document in documents])
        
        if name and version:
            document = Document.query.filter_by(name=name, version=version).first()
            return jsonify(document.serialize())
        
        return jsonify({'error': 'Missing query parameter'}), 400

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
